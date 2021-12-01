import logging
import os


class LoggingConfig(object):
    def __init__(self):
        self.time = True
        self.level_name = True
        self.module = True
        self.process = False
        self.thread = False


class LoggerFactory(object):
    @staticmethod
    def generate_logger(log_path, config: LoggingConfig = LoggingConfig()) -> logging.Logger:
        LoggerFactory._set_up_log_folder(log_path)
        logger = logging.getLogger(log_path)
        logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        logging_format = LoggerFactory._get_format(config)

        formatter = logging.Formatter(logging_format, datefmt="%d-%b-%y %H:%M:%S")

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    @classmethod
    def _get_format(cls, config: LoggingConfig) -> str:
        result = "%(message)s"

        if config.module:
            result = "[%(module)s] " + result
        if config.thread:
            result = "[Thread: %(thread)d] " + result
        if config.process:
            result = "[Process: %(process)d] " + result
        if config.level_name:
            result = "[%(levelname)s] " + result
        if config.time:
            result = "[%(asctime)s] " + result

        return result

    @classmethod
    def _set_up_log_folder(cls, log_path):
        log_folder = os.path.dirname(log_path)
        if not os.path.isdir(log_path):
            os.makedirs(log_folder, exist_ok=True)
