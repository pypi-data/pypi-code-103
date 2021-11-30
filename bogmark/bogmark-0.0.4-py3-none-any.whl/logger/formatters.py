import json
import logging.config
import platform
import traceback
from datetime import datetime

from bogmark.structures.context import get_current_request_id

from .styles import ExtraPercentStyle
from .tools import flatten, get_extra_dict

LEVELS = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARN: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}
REVERSED_LEVELS = {v: k for k, v in LEVELS.items()}

HOST = platform.uname()[1]

logging.config.dictConfig(
    {
        "version": 1,
    }
)


class ExtraFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt, style="%")
        self._style = ExtraPercentStyle(fmt)
        self._fmt = self._style._fmt
        self.datefmt = datefmt

    default_time_format = "%Y-%m-%d %H:%M:%S"
    default_msec_format = "%s,%03d"


class JsonFormatter(logging.Formatter):
    def format(self, rec):  # noqa
        message_name = rec.getMessage()
        log = {
            "@timestamp": datetime.utcfromtimestamp(rec.created).isoformat() + "Z",
            "message": message_name,
            "source_host": HOST,
            "request_id": get_current_request_id(),
            "pid": rec.process,
            "thread": rec.thread,
            "log_level": LEVELS.get(rec.levelno),
            "name": rec.name,
            "line_no": rec.lineno,
            "process_name": rec.processName,
            "thread_name": rec.threadName,
        }

        extra_dict = get_extra_dict(rec)
        if extra_dict:
            log["extra"] = extra_dict

        if rec.exc_info:
            e_type, value, tb = rec.exc_info
            log["error"] = {
                "name": message_name,
                "message": repr(value),
                "traceback": "".join(traceback.format_exception(e_type, value, tb)),
            }
        return json.dumps(flatten(log, sep=":"), ensure_ascii=False)
