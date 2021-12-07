
base_logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            '()': 'coloredlogs.ColoredFormatter',  # colored output

            "format": "[%(asctime)s] %(levelname)s :%(name)s:%(lineno)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "complex": {
            '()': 'coloredlogs.ColoredFormatter',  # colored output
            "format": "[%(asctime)s] %(levelname)s [%(module)s %(name)s :%(lineno)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "complex",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "info_console": {
            "class": "logging.StreamHandler",
            "formatter": "complex",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "db": {
            "class": "pycontainerutils.logger.db.DB_handler.DatabaseHandler",
            "level": "NOTSET",
        },
        # "errors_file": {
        #     "class": "logging.FileHandler",
        #     "filename": "logs/error.log",
        #     "formatter": "complex",
        #     "level": "WARNING",
        # },
        # "all_file": {
        #     "class": "logging.handlers.TimedRotatingFileHandler",
        #     "level": "DEBUG",
        #     "formatter": "complex",
        #     "filename": "logs/all/all.log",
        #     "when": "midnight",
        #     "backupCount": 30,
        #     "interval": 1,
        #     "encoding": "utf-8"
        # },
    },
}