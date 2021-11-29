import logging
import os
import sys
import traceback

from logging import getLogger as getLoggerNative

from sentry_sdk.api import capture_exception


def get_logger(logger_name):
    log_level = os.getenv("LOG_LEVEL", "INFO")

    stage = os.getenv("STAGE")
    if stage in ["local", "test"]:
        return local_logger(logger_name, log_level)

    return lambda_logger(logger_name, log_level)


def local_logger(logger_name, log_level):
    mylogger = logging.getLogger(logger_name)

    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    level = getattr(logging, log_level)
    handler.setLevel(level)

    mylogger.addHandler(handler)
    mylogger.setLevel(level)
    return mylogger


def lambda_logger(logger_name, log_level):
    logger = getLoggerNative(logger_name)

    if log_level:
        logger.setLevel(getattr(logging, log_level))
    else:
        logger.setLevel(logging.ERROR)

    return logger


def send_exception_to_sentry(e: Exception, show_traceback: bool = True):
    if show_traceback:
        traceback.print_exc()
    capture_exception(e)
