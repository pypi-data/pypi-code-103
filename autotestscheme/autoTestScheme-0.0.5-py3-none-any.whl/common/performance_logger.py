import logging
import os
from logging.handlers import RotatingFileHandler
from . import constant


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

if not os.path.exists(constant.PERFORMANCE_LOG_DIR):
    os.makedirs(constant.PERFORMANCE_LOG_DIR)
logFile = os.path.join(constant.PERFORMANCE_LOG_DIR, 'performance.log')

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=200, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)