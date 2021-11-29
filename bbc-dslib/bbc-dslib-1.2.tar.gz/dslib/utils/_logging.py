import logging
import os
import sys
from contextlib import contextmanager
from time import time
from typing import Optional

from humanfriendly import format_timespan


def log(message: str, logger: Optional[logging.Logger] = None, level: int = logging.INFO) -> None:
    """
    Logs a message at the provided level, or prints it if no logger is provided.
    :param message: message to be logged
    :param logger: logger to be used for logging. If None, then "print" function is used
    :param level: logger level to be used when a logger is provided. Defaults to logging.INFO
    :return: None
    """
    if logger:
        logger.log(msg=message, level=level)
    else:
        print(message)


def configure_logging(level: int = logging.INFO, detailed: bool = False,
                      logger: Optional[logging.Logger] = None) -> None:
    """
    Configure basic logging.
    :param level: default level to be set for the logging configuration. Defaults to logging.INFO
    :param detailed: whether the log format should be detailed of not. Defaults to False
    :param logger: whether the log format should be detailed of not. Defaults to False
    :return: None
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Create formatter
    if detailed:
        date_format = '%Y-%m-%d %H:%M:%S'
        log_format = '[%(asctime)s][%(levelname)-8s][%(name)-12s]: %(message)s'
    else:
        date_format = '%H:%M:%S'
        log_format = '%(asctime)s %(levelname)-8s %(message)s'
    formatter = logging.Formatter(log_format, datefmt=date_format)
    # Create sh handler
    handler_sh = logging.StreamHandler(sys.stdout)
    handler_sh.setLevel(level)
    # Add formatter to handler, and handler to root logger
    handler_sh.setFormatter(formatter)
    if root_logger.hasHandlers():
        root_logger.handlers = []
    root_logger.addHandler(handler_sh)
    # Confirm logging was set
    log('Logging was successfully set', logger=logger)


@contextmanager
def timeit(logger: Optional[logging.Logger] = None, text: str = 'Processing took'):
    """
    Context manager and decorator to print or log processing time.
    :param logger: if provided, will be used to log processing time. Otherwise, "print" function is used
    :param text: text to log (will be followed by the time to process, e.g. " 3.2 seconds")
    :return: None
    """
    start = time()
    try:
        yield
    except Exception as e:
        raise e
    else:
        time_span = time() - start
        detailed = time_span < 0.1
        time_span_formatted = format_timespan(time_span, detailed=detailed) or '0 milliseconds'
        log(f'{text.strip()} {time_span_formatted}', logger)


@contextmanager
def suppress_stdout():
    """
    Context manager and decorator to hide stdout of a part of your code. Can be used on prints.
    :return: None
    """
    original_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, 'w')
        yield
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout


class deep_suppress_stdout_stderr(object):
    """
    Context manager doing a "deep suppression" of stdout and stderr, i.e. will suppress all print, even if the print
    originates in a compiled C/Fortran sub-function. This will not suppress raised exceptions, since exceptions are
    printed to stderr just before a script exits, and after the context manager has exited.
    Copied from: https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
    """
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)
