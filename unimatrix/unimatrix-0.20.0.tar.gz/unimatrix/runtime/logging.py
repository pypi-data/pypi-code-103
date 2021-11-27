"""Specifies the default logging configuration for Unimatrix
applications.
"""
import copy
import logging.config
import os


DEFAULT_LOG_LEVEL = 'ERROR'

SYSLOG_HOST = os.getenv('SYSLOG_HOST') or 'localhost'

SYSLOG_PORT = int(os.getenv('SYSLOG_PORT') or 5140)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            'datefmt': "[%Y-%m-%d %H:%M:%S %z]"
        },
        'simple_syslog': {
            'format': "%(message)s\n"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'user',
            'formatter': 'simple_syslog',
            'address' : (SYSLOG_HOST, SYSLOG_PORT),
        },
    },
    'loggers': {
        'unimatrix': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL),
        },
        'unimatrix.io': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL),
            'propagate': False
        },
    }
}


def configure(loggers=None):
    """Configure loggers."""
    defaults = copy.deepcopy(LOGGING)
    defaults['loggers'].update(loggers or {})
    logging.config.dictConfig(defaults)
