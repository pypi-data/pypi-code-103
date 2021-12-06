import gevent.monkey
gevent.monkey.patch_all()
from . import common
from loguru import logger
from . import start_data
import os
import logging
import sys


class PropogateHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logging.getLogger(record.name).handle(record)


@common.singleton
class Logger(object):

    def __init__(self):
        self.trace = self.get_trace()
        logger.add(PropogateHandler(), format="{time:YYYY-MM-DD at HH:mm:ss} | {message}")

    def get_trace(self):
        return logger.add(self.get_log_path(), level='DEBUG', rotation="200 MB")

    def get_log_path(self):
        log_folder = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_path = os.path.join(start_data.LOGGER_FOLDER, start_data.Logger_START_STR + '_{time}.log')
        return log_path

    def restart(self):
        logger.remove(self.trace)
        self.trace = self.get_trace()


_logger = Logger()
restart = _logger.restart
debug = logger.debug
info = logger.info
error = logger.error
warning = logger.warning
exception = logger.exception


