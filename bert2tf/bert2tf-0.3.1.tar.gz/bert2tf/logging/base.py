import logging
import os
import re
import sys
from copy import copy
from logging import Formatter
from typing import Union

from ..enums import LogVerbosity
from ..helper import colored


class ColorFormatter(Formatter):
    """Format the log into colored logs based on the log-level. """

    MAPPING = {
        'DEBUG': dict(color='white', on_color=None),  # white
        'INFO': dict(color='white', on_color=None),  # cyan
        'WARNING': dict(color='yellow', on_color='on_grey'),  # yellow
        'ERROR': dict(color='red', on_color=None),  # 31 for red
        'CRITICAL': dict(color='white', on_color='on_red'),  # white on red bg
        'SUCCESS': dict(color='green', on_color=None),  # white on red bg
    }  #: log-level to color mapping

    def format(self, record):
        cr = copy(record)
        seq = self.MAPPING.get(cr.levelname, self.MAPPING['INFO'])  # default white
        cr.msg = colored(cr.msg, **seq)
        return super().format(cr)


def get_logger(context: str,
               context_len: int = 15,
               fmt_str: str = None,
               **kwargs) -> Union['logging.Logger', 'NTLogger']:
    """Get a logger with configurations

    :param context: the name prefix of the log
    :param context_len: length of the context, i.e. module, function, line number
    :param fmt_str: use customized logging format, otherwise respect the ``BERT2TF_LOG_LONG`` environment variable
    :return: the configured logger

    .. note::
        One can change the verbosity of bert2tf logger via the environment variable ``BERT2TF_LOG_VERBOSITY``

    """
    if not fmt_str:
        fmt_str = f'{context[:context_len]:>{context_len}}@%(process)2d' \
                  f'[%(levelname).1s]:%(message)s'

    verbose_level = LogVerbosity.from_string(os.environ.get('BERT2TF_LOG_VERBOSITY', 'INFO'))

    if os.name == 'nt':  # for Windows
        return NTLogger(context, verbose_level)

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(context)
    logger.propagate = False
    logger.handlers = []
    logger.setLevel(verbose_level.value)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter(fmt_str))
    logger.addHandler(console_handler)

    success_level = LogVerbosity.SUCCESS.value  # between WARNING and INFO
    logging.addLevelName(success_level, 'SUCCESS')
    setattr(logger, 'success', lambda message: logger.log(success_level, message))

    return logger


class NTLogger:
    def __init__(self, context: str, log_level: 'LogVerbosity'):
        """A compatible logger for Windows system, colors are all removed to keep compat.

        :param context: the name prefix of each log
        :param log_level: show debug level info
        """
        self.context = self._planify(context)
        self.log_level = log_level

    @staticmethod
    def _planify(msg: str):
        return re.sub(u'\u001b\[.*?[@-~]', '', msg)

    def info(self, msg: str, **kwargs):
        """log info-level message"""
        if self.log_level <= LogVerbosity.INFO:
            sys.stdout.write(f'I:{self.context}:{self._planify(msg)}')

    def critical(self, msg: str, **kwargs):
        """log critical-level message"""
        if self.log_level <= LogVerbosity.CRITICAL:
            sys.stdout.write(f'C:{self.context}:{self._planify(msg)}')

    def debug(self, msg: str, **kwargs):
        """log debug-level message"""
        if self.log_level <= LogVerbosity.DEBUG:
            sys.stdout.write(f'D:{self.context}:{self._planify(msg)}')

    def error(self, msg: str, **kwargs):
        """log error-level message"""
        if self.log_level <= LogVerbosity.ERROR:
            sys.stdout.write(f'E:{self.context}:{self._planify(msg)}')

    def warning(self, msg: str, **kwargs):
        """log warn-level message"""
        if self.log_level <= LogVerbosity.WARNING:
            sys.stdout.write(f'W:{self.context}:{self._planify(msg)}')

    def success(self, msg: str, **kwargs):
        """log success-level message"""
        if self.log_level <= LogVerbosity.SUCCESS:
            sys.stdout.write(f'W:{self.context}:{self._planify(msg)}')
