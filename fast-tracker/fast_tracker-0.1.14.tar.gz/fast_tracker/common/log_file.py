# -*- coding: utf-8 -*-

import sys
import logging
import threading

_lock = threading.Lock()


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass


_agent_logger = logging.getLogger('fast')
_agent_logger.addHandler(_NullHandler())

_LOG_FORMAT = '%(asctime)s (%(process)d/%(threadName)s) ' \
              '%(name)s %(levelname)s - %(message)s'

_initialized = False


def _initialize_stdout_logging(log_level):
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(_LOG_FORMAT)
    handler.setFormatter(formatter)

    _agent_logger.addHandler(handler)
    _agent_logger.setLevel(log_level)

    _agent_logger.debug('正在初始化Python代理的日志输出.')


def _initialize_stderr_logging(log_level):
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(_LOG_FORMAT)
    handler.setFormatter(formatter)

    _agent_logger.addHandler(handler)
    _agent_logger.setLevel(log_level)

    _agent_logger.debug('正在初始化Python代理的错误日志输出.')


def _initialize_file_logging(log_file, log_level):
    handler = logging.FileHandler(log_file)

    formatter = logging.Formatter(_LOG_FORMAT)
    handler.setFormatter(formatter)

    _agent_logger.addHandler(handler)
    _agent_logger.setLevel(log_level)

    _agent_logger.debug('正在初始化Python代理的日志.')
    _agent_logger.debug('日志文件 "%s".' % log_file)


def initialize_logging(log_file, log_level):
    global _initialized

    if _initialized:
        return

    _lock.acquire()

    try:
        if log_file == 'stdout':
            _initialize_stdout_logging(log_level)

        elif log_file == 'stderr':
            _initialize_stderr_logging(log_level)

        elif log_file:
            try:
                _initialize_file_logging(log_file, log_level)

            except Exception:
                _initialize_stderr_logging(log_level)

                _agent_logger.exception('无法创建日志文件.' % log_file)

        _initialized = True

    finally:
        _lock.release()


class RequestsConnectionFilter(logging.Filter):
    def filter(self, record):
        return False


_requests_logger = logging.getLogger(
    'fast-tracker.packages.requests.packages.urllib3.connectionpool')
_requests_logger.addFilter(RequestsConnectionFilter())
