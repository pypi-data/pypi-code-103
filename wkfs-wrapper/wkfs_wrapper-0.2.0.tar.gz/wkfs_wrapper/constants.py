"""Module for storing constants for the CSC Recorder package"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "development": {
            "format": (
                "%(process)d  %(thread)d  %(asctime)-25s %(module)-15s %(funcName)-30s %(levelname)-10s -  %(message)s"
            ),
        },
    },
    "handlers": {
        "development": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "development",
        },
    },
    "loggers": {
        "csc-recorder": {
            "handlers": ["development"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
