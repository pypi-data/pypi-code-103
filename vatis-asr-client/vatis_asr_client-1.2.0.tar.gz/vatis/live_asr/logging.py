import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Callable

import vatis.live_asr.config_variables as config_variables

FORMATTER = logging.Formatter("%(asctime)s — %(threadName)s — %(process)d — %(name)s — %(levelname)s — %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(config_variables.LOGS_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def create_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    if config_variables.LOGS_FILE_ENABLED:
        logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


"""
To configure the logging of this library, override this value 
"""
LOGGER_FACTORY_METHOD: Callable[[str], logging.Logger] = create_logger


def get_logger(logger_name: str) -> logging.Logger:
    return LOGGER_FACTORY_METHOD(logger_name)


def print_if_debugging(logger, msg, *args):
    if config_variables.DEBUG:
        logger.info(msg, args)
