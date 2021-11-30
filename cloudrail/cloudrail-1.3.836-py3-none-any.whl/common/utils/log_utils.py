import functools
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict


class SensitiveFilter(logging.Filter):
    def filter(self, record):
        return not re.search('api-key|api_key|password|role_name|external_id|apiKey', record.getMessage())


class WarningsFilter(logging.Filter):
    def filter(self, record):
        return not re.search('DeprecationWarning|UserWarning', record.getMessage())


class LogUtils:
    local_loader = None

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_log_level_aliases() -> Dict[str, int]:
        return {
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL,
            'ERROR': logging.ERROR,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET
        }

    @staticmethod
    def init_logger(log_level=logging.INFO):
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addFilter(SensitiveFilter())
        logger.addFilter(WarningsFilter())

    @staticmethod
    def init_file_logger():
        logger_file = os.getenv('LOGFILE', os.path.join(Path.home(), '.cloudrail', 'cloudrail.cli.log'))
        logger_dir = os.path.dirname(logger_file)
        os.makedirs(logger_dir, exist_ok=True)
        logger = logging.getLogger()
        handler = RotatingFileHandler(logger_file, maxBytes=10000000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @classmethod
    def init_local_logger(cls):
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        cls.local_loader = LocalLogger()
        log_handler = cls.local_loader.log_handler
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

    @classmethod
    def get_local_logger_data(cls):
        return cls.local_loader.contents() if cls.local_loader else ''


class LocalLogHandler(logging.Handler):

    def __init__(self, log_queue):
        logging.Handler.__init__(self)
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.append(self.format(record))


class LocalLogger:

    def __init__(self):
        self._log_queue = []
        self._log_handler = LocalLogHandler(self._log_queue)

    def contents(self):
        return '\n'.join(self._log_queue) if self._log_queue else ''

    @property
    def log_handler(self):
        return self._log_handler
