"""
Structured logging.

This module defines functions to setup the standard Python logging subsystem to do one of the
two things:

- Output the regular logs with color and arguably proper format. This is good for running your
  application locally, for debugging purposes.
- Output JSON objects for each logging call, one line per object ("structured logging"). This
  mode should be used when running in production so that the logs can be easily parsed.

You can setup everything using:

- `add_logging_args()` as argparse.ArgumentParser initialization time and forget about it.
- call `setup()` and specify the logging level and mode.
"""

import argparse
import base64
import codecs
import datetime
import functools
import io
import json
import logging
import lzma
import math
import os
import re
import sys
import threading
import traceback
from typing import Callable, Optional, Tuple, Union
import uuid

import xxhash


try:
    from numpy import ndarray, set_string_function as np_set_string_function
    from numpy.core.arrayprint import _default_array_repr
except ImportError:
    import warnings

    warnings.warn("numpy is not installed. Please install numpy to log numpy arrays.")

    class ndarray:
        pass

    def np_set_string_function(*args, **kwargs):
        return

    def _default_array_repr(*args, **kwargs):
        return ""


logs_are_structured = False


def get_datetime_now() -> datetime:
    """Return the current UTC date and time."""
    return datetime.datetime.now(datetime.timezone.utc)


def get_timezone() -> Tuple[datetime.tzinfo, str]:
    """Discover the current time zone and it's standard string representation."""
    dt = get_datetime_now().astimezone()
    tzstr = dt.strftime("%z")
    tzstr = tzstr[:-2] + ":" + tzstr[-2:]
    return dt.tzinfo, tzstr


timezone, tzstr = get_timezone()
_now = get_datetime_now()
if _now.month == 12:
    _fest = "🎅 "
elif _now.month == 10 and _now.day > (31 - 7):
    _fest = "🎃 "
elif _now.month == 5 and _now.day == 1:
    _fest = "🔨 "
elif _now.month == 3 and _now.day == 8:
    _fest = "👩 "
else:
    _fest = ""
del _now


def format_datetime(dt: datetime.datetime):
    """Represent the date and time in standard format."""
    return dt.strftime("%Y-%m-%dT%k:%M:%S.%f000") + tzstr


def reduce_thread_id(thread_id: int) -> str:
    """Make a shorter thread identifier by hashing the original."""
    return xxhash.xxh32(thread_id.to_bytes(8, "little")).hexdigest()[:4]


def repr_array(arr: ndarray) -> str:
    """repr() with shape."""
    return "array(shape=%r, %s" % (arr.shape, _default_array_repr(arr).split("(", 1)[1])


def with_logger(cls):
    """Add a logger as static attribute to a class."""
    cls._log = logging.getLogger(cls.__name__)
    return cls


trailing_dot_exceptions = set()


def check_trailing_dot(func: Callable) -> Callable:
    """
    Decorate a function to check if the log message ends with a dot.

    AssertionError is raised if so.
    """

    @functools.wraps(func)
    def decorated_with_check_trailing_dot(*args):
        # we support two signatures: (self, record) and (record)
        record = args[-1]
        if record.name not in trailing_dot_exceptions:
            msg = record.msg
            if isinstance(msg, str) and msg.endswith(".") and not msg.endswith(".."):
                raise AssertionError(
                    'Log message is not allowed to have a trailing dot: %s: "%s"'
                    % (record.name, msg),
                )
        args = list(args)
        args[-1] = record
        return func(*args)

    return decorated_with_check_trailing_dot


class AwesomeFormatter(logging.Formatter):
    """logging.Formatter which adds colors to messages and shortens thread ids."""

    GREEN_MARKERS = [
        "ok",
        "finished",
        "complete",
        "ready",
        "done",
        "running",
        "success",
        "saved",
        "loaded",
    ]
    GREEN_RE = re.compile("(?<![_a-zA-Z0-9])(%s)(?![_a-zA-Z0-9])" % "|".join(GREEN_MARKERS))

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Convert the already filled log record to a string."""
        level_color = "0"
        text_color = "0"
        fmt = ""
        if record.levelno <= logging.DEBUG:
            fmt = "\033[0;37m" + logging.BASIC_FORMAT + "\033[0m"
        elif record.levelno <= logging.INFO:
            level_color = "1;36"
            lmsg = record.message.lower()
            if self.GREEN_RE.search(lmsg):
                text_color = "1;32"
        elif record.levelno <= logging.WARNING:
            level_color = "1;33"
        elif record.levelno <= logging.CRITICAL:
            level_color = "1;31"
        if not fmt:
            fmt = (
                "\033["
                + level_color
                + "m%(levelname)s\033[0m:%(rthread)s:%(name)s:\033["
                + text_color
                + "m%(message)s\033[0m"
            )
        fmt = _fest + fmt
        record.rthread = reduce_thread_id(record.thread)
        return fmt % record.__dict__


class StructuredHandler(logging.Handler):
    """logging handler for structured logging."""

    def __init__(
        self, level=logging.NOTSET, level_from_msg: Optional[Callable[[str], Optional[str]]] = None
    ):
        """Initialize a new StructuredHandler."""
        super().__init__(level)
        self.local = threading.local()
        self.level_from_msg = level_from_msg if level_from_msg is not None else lambda _: None

    @check_trailing_dot
    def emit(self, record: logging.LogRecord):
        """Print the log record formatted as JSON to stdout."""
        created = datetime.datetime.fromtimestamp(record.created, timezone)
        msg = self.format(record)
        level = self.level_from_msg(msg)
        if level is None:
            level = record.levelname.lower()
        else:
            level = level.lower()
        if msg.startswith("{"):
            try:
                msg = json.loads(msg)
            except json.JSONDecodeError:
                pass
        obj = {
            "level": level,
            "msg": msg,
            "source": "%s:%d" % (record.filename, record.lineno),
            "time": format_datetime(created),
            "thread": reduce_thread_id(record.thread),
            "name": record.name,
        }
        if record.exc_info is not None:
            try:
                obj["error"] = traceback.format_exception(*record.exc_info)[1:]
            except TypeError:
                obj["error"] = record.exc_info
        try:
            obj["context"] = self.local.context
        except AttributeError:
            pass
        json.dump(obj, sys.stdout, sort_keys=True)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def flush(self):
        """Write all pending text to stdout."""
        sys.stdout.flush()


def setup(
    level: Optional[Union[str, int]] = os.environ.get("LOG_LEVEL", "INFO"),  # noqa: B008
    structured: bool = os.getenv("LOG_STRUCTURED", False),  # noqa: B008
    allow_trailing_dot: bool = False,
    level_from_msg: Optional[Callable[[str], Optional[str]]] = None,
) -> None:
    """
    Make stdout and stderr unicode friendly in case of configured \
    environments, initializes the logging, structured logging and \
    enables colored logs if it is appropriate.

    :param level: Global logging level (case insensitive).
    :param structured: Output JSON logs to stdout.
    :param allow_trailing_dot: Value indicating whether to not raise an exception \
                               when a logging message ends with a dot.
    :param level_from_msg: Customize the logging level depending on the formatted message. \
                           Returning None means no change of the level.
    :return: Nothing.
    """
    global logs_are_structured
    logs_are_structured = structured

    if not isinstance(level, int):
        level = logging._nameToLevel[level.upper()]

    def ensure_utf8_stream(stream):
        if not isinstance(stream, io.StringIO) and hasattr(stream, "buffer"):
            stream = codecs.getwriter("utf-8")(stream.buffer)
            stream.encoding = "utf-8"
        return stream

    sys.stdout, sys.stderr = (ensure_utf8_stream(s) for s in (sys.stdout, sys.stderr))
    np_set_string_function(repr_array)

    # basicConfig is only called to make sure there is at least one handler for the root logger.
    # All the output level setting is down right afterwards.
    logging.basicConfig()
    logging.captureWarnings(True)
    for key, val in os.environ.items():
        if key.startswith("flog_"):
            domain = key[len("flog_") :]
            logging.getLogger(domain).setLevel(logging._nameToLevel.get(val, level))
    root = logging.getLogger()
    root.setLevel(level)

    if not structured:
        handler = root.handlers[0]
        if not allow_trailing_dot:
            handler.emit = check_trailing_dot(handler.emit)
        # pytest injects DontReadFromInput which does not have "closed"
        if not getattr(sys.stdin, "closed", False) and sys.stdout.isatty():
            handler.setFormatter(AwesomeFormatter())
    else:
        root.handlers[0] = StructuredHandler(level, level_from_msg)


def set_context(context):
    """Assign the logging context - an abstract object - to the current thread."""
    try:
        handler = logging.getLogger().handlers[0]
    except IndexError:
        # logging is not initialized
        return
    if not isinstance(handler, StructuredHandler):
        return
    handler.acquire()
    try:
        handler.local.context = context
    finally:
        handler.release()


def add_logging_args(
    parser: argparse.ArgumentParser,
    patch: bool = True,
    erase_args: bool = True,
    allow_trailing_dot: bool = False,
    level_from_msg: Optional[Callable[[str], Optional[str]]] = None,
) -> None:
    """
    Add command line flags specific to logging.

    :param parser: `argparse` parser where to add new flags.
    :param erase_args: Automatically remove logging-related flags from parsed args.
    :param patch: Patch parse_args() to automatically setup logging.
    :param allow_trailing_dot: Value indicating whether to not raise an exception \
                               when a logging message ends with a dot.
    :param level_from_msg: Customize the logging level depending on the formatted message. \
                           Returning None means no change of the level.
    """
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=logging._nameToLevel,
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--log-structured",
        action="store_true",
        help="Enable structured logging (JSON record per line).",
    )
    # monkey-patch parse_args()
    # custom actions do not work, unfortunately, because they are not invoked if
    # the corresponding --flags are not specified

    def _patched_parse_args(args=None, namespace=None) -> argparse.Namespace:
        args = parser._original_parse_args(args, namespace)
        setup(
            args.log_level,
            args.log_structured,
            allow_trailing_dot=allow_trailing_dot,
            level_from_msg=level_from_msg,
        )
        if erase_args:
            for log_arg in ("log_level", "log_structured"):
                delattr(args, log_arg)
        return args

    if patch and not hasattr(parser, "_original_parse_args"):
        parser._original_parse_args = parser.parse_args
        parser.parse_args = _patched_parse_args


def log_multipart(log: logging.Logger, data: bytes) -> str:
    """
    Log something big enough to be compressed and split in pieces.

    :return: Log record ID that we can later search for.
    """
    data = base64.b64encode(lzma.compress(data)).decode()
    record_id = str(uuid.uuid4())
    chunk_size = 32000  # Google's limit on overall record size is 32768
    chunks = int(math.ceil(len(data) / chunk_size))
    for i in range(chunks):
        log.info(
            "%d / %d %s %s",
            i + 1,
            chunks,
            record_id,
            data[chunk_size * i : chunk_size * (i + 1)],
        )
    return record_id
