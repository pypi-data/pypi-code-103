"""Logging utility.

Classes:
LoggerContext - Interface for this module's Logger.

Functions:
start_logger - Creates a new Logger instance.
"""

import logging
import sys
LOG_SUFFIX = '.log'
from eagers.config.path_spec import USER_DIR_SIMRESULTS


class LoggerContext:
    """The interface for this module's Logger. This class exists so the
    name "logger" can be imported from this module. If the Logger for
    this module has been initialized it will pass any attribute and
    method calls on to that Logger. Otherwise, an AttributeError will be
    raised with the message that the Logger for this module has not been
    started.
    """
    def __init__(self):
        self.logger_started = False

    def __getattr__(self, name):
        if not self.logger_started:
            raise AttributeError(f"Logger not started for module {__name__!r}")
        return getattr(self.logger, name)

    @property
    def logger(self):
        # Return this module's Logger via the logging module.
        return logging.getLogger(__name__)

    def logger_ready(self):
        self.logger_started = True

    def close(self):
        """Clean up resources."""
        logger = logging.getLogger(__name__)
        # Must make a copy of the handlers attribute; otherwise the for
        # loop will misbehave when the list it's referencing changes.
        handlers = logger.handlers[:]
        for hlr in handlers:
            hlr.close()
            logger.removeHandler(hlr)


logger = LoggerContext()


def start_logger(filename, out_stream=None):
    """Factory function for creating a Logger instance within this
    module.

    Positional arguments:
    filename - (str) Name of log file.

    Keyword arguments:
    out_stream - (stream) (Default: None) Output stream. If not
        specified, will default to stdout.
    """
    # Handle input.
    if not out_stream:
        out_stream = sys.stdout

    # Set up logging.  This Logger will output both to a file and the
    # console, via whichever stream is specified.  Two such Handlers are
    # added to it.
    logpath = USER_DIR_SIMRESULTS / f"{filename}{LOG_SUFFIX}"
    hlr_file = logging.FileHandler(logpath)
    hlr_file.setLevel(logging.DEBUG)
    hlr_outstream = logging.StreamHandler(out_stream)
    hlr_outstream.setLevel(logging.DEBUG)
    # Filter out traceback messages from the output stream Handler.
    # Raised Exceptions are already printed to the stream.
    no_exc = (
        lambda r:
        "Traceback (most recent call last):" not in r.getMessage()
    )
    hlr_outstream.addFilter(no_exc)
    lgr = logging.getLogger(__name__)
    lgr.setLevel(logging.DEBUG)
    lgr.addHandler(hlr_file)
    lgr.addHandler(hlr_outstream)
    fmr_file = logging.Formatter(
        fmt="{asctime} {levelname}: {message}",
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
    )
    hlr_file.setFormatter(fmr_file)

    # Allow access to the logger via this module's "logger" attribute.
    logger.logger_ready()
