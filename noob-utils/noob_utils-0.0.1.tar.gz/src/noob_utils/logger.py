import logging
import sys

from colorama import init
from colorama import Fore, Back


init(autoreset=True)

def fmt_filter(record):
    record.levelname = '[%s]' % record.levelname
    record.name = '[%s]' % record.name
    return True

class CustomFormatter(logging.Formatter):

    FORMATS = {
        logging.DEBUG: [Fore.LIGHTBLACK_EX, Fore.RESET],
        logging.INFO: [Fore.GREEN, Fore.RESET],
        logging.WARNING: [Fore.YELLOW, Fore.RESET],
        logging.ERROR: [Fore.MAGENTA, Fore.RESET],
        logging.CRITICAL: [Back.RED, Back.RESET]
    }

    def format(self, record):
        log_color = self.FORMATS.get(record.levelno)
        log_fmt = f"{Fore.CYAN}[%(asctime)s]{Fore.RESET} {log_color[0]}%(levelname)-10s{log_color[1]} {Fore.LIGHTCYAN_EX}%(name)-15s{Fore.RESET} %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addFilter(fmt_filter)
    return logger