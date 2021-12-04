"""Provides a configurable logging facility for the supermodels package."""
import logging

from supermodels.config import LOG_FORMAT, LOG_LEVEL


def get_logger(name) -> logging.Logger:
    """Returns a configurable logger."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(LOG_LEVEL)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)

    return logger
