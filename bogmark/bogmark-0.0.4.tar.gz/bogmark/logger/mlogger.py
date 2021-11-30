import inspect
import logging
import sys
import traceback
from collections.abc import Iterable
from logging import getLevelName

from .formatters import ExtraFormatter, JsonFormatter
from .tools import disable_noise

_LOGGER_INIT_INFO = None


def init_logger(is_debug: bool = False, level: str = "INFO", noisy_loggers: Iterable = ()):
    # The logger can only be initialized once
    global _LOGGER_INIT_INFO
    prev_frame = inspect.stack()[1]
    if _LOGGER_INIT_INFO is not None:
        raise RuntimeError(
            f"Attempt to reinitialization the logger. "
            f"Current call from {prev_frame.filename} line {prev_frame.lineno}. "
            f"First call from {_LOGGER_INIT_INFO['filename']} line {_LOGGER_INIT_INFO['lineno']}"
        )
    _LOGGER_INIT_INFO = {"filename": prev_frame.filename, "lineno": prev_frame.lineno}

    logger = logging.getLogger()
    logger.handlers = []
    log_handler = logging.StreamHandler()
    if is_debug:
        log_handler.setFormatter(ExtraFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.setLevel(level)
    else:
        disable_noise(noisy_loggers)
        log_handler.stream = sys.stdout
        log_handler.setFormatter(JsonFormatter())
        logger.setLevel(getLevelName(level))

        def except_hook(*args):
            exc_type, value, current_traceback = args
            formatted_traceback = "".join(traceback.format_exception(exc_type, value, current_traceback))
            logger.critical(formatted_traceback, exc_info=True)

        sys.excepthook = except_hook
    logger.addHandler(log_handler)

    return logger


def get_logger(module, name=None):
    logger_fqn = module
    if name is not None:
        if inspect.isclass(name):
            name = name.__name__
        logger_fqn += "." + name
    logger = logging.getLogger(logger_fqn)
    return logger
