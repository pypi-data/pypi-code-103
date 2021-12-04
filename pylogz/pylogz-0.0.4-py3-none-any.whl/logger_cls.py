import os
import sys
import logging
import threading
from typing import Dict, Any, Union, List
from types import MethodType
from .utils import convert_log

_notebook = sys.argv[-1].endswith('json')
_logging_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'warning': logging.WARNING,
    'error': logging.ERROR,
}

_logger_name: str = None
_logger_handler: logging.Logger = None
_logger_lock = threading.Lock()
_logger_multi: bool = bool(os.getenv('PYLOGZ_MULTI_LOGGER', 'true').lower() in {'true', 'yes', '1'})
_logger_default_loglevel: str = os.getenv('PYLOGZ_LOGLEVEL', 'info')
_logger_cls_name: str = os.getenv('PYLOGZ_CLS_NAME', 'logz')
_logger_dtime_format: str = os.getenv('PYLOGZ_DTIME_FORMAT', "%Y-%m-%d %H:%M:%SZ")
_logger_color_enabled: bool = bool(os.getenv('PYLOGZ_COLOR_DISABLED', 'false').lower() not in {'true', 'yes', '1'})
_logger_console_log_output: str = os.getenv('PYLOGZ_CONSOLE_LOG_OUTPUT', 'stdout')
_logger_log_line_template: str = os.getenv('PYLOGZ_LOGLINE_TEMPLATE', "%(asctime)s [<cls_name>] %(color_on)s%(module)s.%(funcName)-20s%(color_off)s %(message)-2s")
_logger_logfile_log_level: str = os.getenv('PYLOGZ_LOGFILE_LOG_LEVEL', 'debug')
_logger_logfile_file: str = os.getenv('PYLOGZ_LOGFILE_FILE', None)
_logger_logfile_log_color: bool = bool(os.getenv('PYLOGZ_LOGFILE_COLOR_ENABLED', 'false').lower() in {'true', 'yes', '1'})
_logger_propagate: bool = bool(os.getenv('PYLOGZ_PROPAGATE', 'true').lower() in {'true', 'yes', '1'})
_logger_clear_handlers: bool = bool(os.getenv('PYLOGZ_CLEAR_HANDLERS', 'false').lower() in {'true', 'yes', '1'})

# Hacky way of making it callable.
def _callable(self, msgs: Union[List[Any], str], split_newline: bool = False, log_level = _logger_default_loglevel, *args, **kwargs):
    if not isinstance(msgs, list): msgs = [msgs]
    log_msgs = convert_log(*msgs, split_newline = split_newline)
    mode = _logging_levels.get(log_level, 'info')
    for msg in log_msgs:
        if msg: self._log(mode, msg, args, **kwargs)

logging.Logger.__call__ = _callable

if _logger_multi: _logger_handler: Dict[str, logging.Logger] = {}

class LogFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.CRITICAL: "\033[38;5;196m", # bright/bold magenta
        logging.ERROR:    "\033[38;5;9m", # bright/bold red
        logging.WARNING:  "\033[38;5;11m", # bright/bold yellow
        logging.INFO:     "\033[38;5;111m", # white / light gray
        logging.DEBUG:    "\033[1;30m"  # bright/bold black / dark gray
    }

    RESET_CODE = "\033[0m"
    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if (self.color == True and record.levelno in self.COLOR_CODES):
            record.color_on  = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on  = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)


def setup_logging(config):
    logger = logging.getLogger(config['name'])
    default_log_level = config.get('log_level', 'info')
    logger.setLevel(_logging_levels[default_log_level])

    console_log_output = sys.stdout if _notebook else sys.stderr        
    console_handler = logging.StreamHandler(console_log_output)
    console_handler.setLevel(config["console_log_level"].upper())
    console_formatter = LogFormatter(fmt=config["log_line_template"], color=config["console_log_color"], datefmt=config.get('datefmt', None))
    console_handler.setFormatter(console_formatter)
    if config.get('clear_handlers', False) and logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(console_handler)
    if config.get('quiet_loggers'):
        to_quiet = config['quiet_loggers']
        if isinstance(to_quiet, str): to_quiet = [to_quiet]
        for clr in to_quiet:
            clr_logger = logging.getLogger(clr)
            clr_logger.setLevel(logging.ERROR)

    logger.propagate = config.get('propagate', False)

    def _logger_callable(self, *msgs, split_newline: bool = False, log_level = default_log_level, **kwargs):
        return self(*msgs, split_newline = split_newline, log_level = log_level, **kwargs)

    setattr(logger, "__call__", MethodType(_logger_callable, logger))
    return logger


def setup_new_logger(name, log_level = _logger_default_loglevel, clear_handlers = _logger_clear_handlers, propagate = _logger_propagate, quiet_loggers = None, **kwargs):
    logger_config = {
        'name': name,
        'log_level': log_level,
        'console_log_output': kwargs.get('console_log_output', _logger_console_log_output), 
        'console_log_level': log_level,
        'console_log_color': kwargs.get('console_log_color', _logger_color_enabled),
        'logfile_file': kwargs.get('logfile_file', _logger_logfile_file),
        'logfile_log_level': kwargs.get('logfile_log_level', _logger_logfile_log_level),
        'logfile_log_color': kwargs.get('logfile_log_color', _logger_logfile_log_color),
        'log_line_template': kwargs.get('log_line_template', _logger_log_line_template).replace('<cls_name>', name),
        'clear_handlers': clear_handlers,
        'quiet_loggers': quiet_loggers,
        'propagate': propagate,
        'datefmt': kwargs.get('datefmt', _logger_dtime_format)
    }
    return setup_logging(logger_config)


def get_logger(name: str = _logger_cls_name, log_level = _logger_default_loglevel, *args, **kwargs):
    global _logger_handler, _logger_name
    with _logger_lock:
        if _logger_multi:
            if not _logger_handler.get(name):
                _logger_handler[name] = setup_new_logger(name = name, log_level=log_level, *args, **kwargs)
            return _logger_handler[name]
        if not _logger_handler:
            _logger_handler = setup_new_logger(name = name, log_level=log_level, *args, **kwargs)
            _logger_name = name
        return _logger_handler


def get_cls_logger(name: str, log_level = _logger_default_loglevel, *args, **kwargs):
    def _get_logger(clsname = name, clslog_level = log_level, clsargs = args, clskwargs = kwargs):
        return get_logger(name = clsname, log_level = clslog_level, *clsargs, **clskwargs)
    return _get_logger
