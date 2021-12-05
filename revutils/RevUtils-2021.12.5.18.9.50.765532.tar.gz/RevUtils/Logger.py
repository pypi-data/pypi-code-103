import logging
import logging.handlers as lh
import os
from datetime import datetime as dt


def make_dirs_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def now_dt_str():
    return dt.now().strftime('%Y-%m-%d.%H-%M-%S')


working_dir = os.getcwd()
logs_dir = f'{working_dir}/logs'

make_dirs_if_not_exists(logs_dir)

# PYTHONUTF8=1
os.environ['PYTHONUTF8'] = '1'

# Logger

# Formatter
formatter = logging.Formatter(u"%(asctime)s:%(levelname)s:%(message)s")

# File Handler
# file_handler=logging.FileHandler(f'{working_dir}/logs/{now_dt_str()}.log', encoding='utf8')

# Timed Rotating File Handler
timed_rotating_handler = lh.TimedRotatingFileHandler(f'{logs_dir}/{now_dt_str()}.log', when='midnight',
                                                     encoding='utf8')
timed_rotating_handler.suffix = '~%Y-%m-%d.%H-%M-%S.log'
timed_rotating_handler.setFormatter(formatter)

# Stream Handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Logger Config
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(timed_rotating_handler)
logger.addHandler(stream_handler)


def debug(text):
    try:
        logging.debug(text)
    except Exception as ex:
        print(ex)


def info(text):
    try:
        logging.info(text)
    except Exception as ex:
        print(ex)


def error(text):
    try:
        logging.error(text)
    except Exception as ex:
        print(ex)
