import logging
import logging.config


DateFormat = "%d/%b/%Y %H:%M:%S"
LogFormatShort = "%(asctime)s :: %(message)s"


logger = logging.getLogger("pytest-db")

if not logger.handlers:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "short": {
                    "format": LogFormatShort,
                    "datefmt": DateFormat,
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "formatter": "short",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "pytest-db": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )
