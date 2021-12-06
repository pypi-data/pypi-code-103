"""logger

This module implements the core logging features to trace program execution

It exports the following functions

 * log_debug(message: str)
    -> logs a message under a debug tag, does not write to a log file
 * log_info(message: str)
    -> logs a message under an info tag, writes to a log file
 * log_error(message: str)
    -> logs a message under an error tag with a stack trace, writes to a log file,
        it includes a stack trace in the log optionally dumps recent debug messages.
        That functionality is configurable in the config file.
"""

import sys

from datetime import datetime
from traceback import format_exception, format_stack
from typing import List

from .config import get_config

# Used to store a history of debug messages
# Used by
#  * log_error
debug_messages: List[str] = []

def log_debug(message: str) -> None:
    """
    Logs a message under a debug tag if debug logging is enabled.
    Does not write to a log file.

    Parameters
    ----------
    message : str
        The message to log
    """

    logging_config = get_config('logging')

    if not logging_config['enabled']:
        return

    prefixed_message = f"<{datetime.now()}> [DEBUG] {message}"

    debug_messages.append(prefixed_message)

    if logging_config['debug']:
        print(prefixed_message, file=sys.stdout)

def log_info(message: str) -> None:
    """
    Logs a message under an info tag if logging is enabled.

    Parameters
    ----------
    message : str
        The message to log
    """

    logging_config = get_config('logging')

    if not logging_config['enabled']:
        return

    prefixed_message = f"<{datetime.now()}> [INFO] {message}"

    print(prefixed_message, file=sys.stdout)

    if logging_config['use_file']:
        with open(logging_config['path'], 'a', encoding='UTF-8') as logfile:
            logfile.write(f"{prefixed_message}\n")

def log_error(message: str, error=None) -> None:
    """
    Logs a message under an error tag if logging is enabled.
    It will include a stack trace in this log.

    Parameters
    ----------
    message : str
        The message to log
    """

    logging_config = get_config('logging')

    if not logging_config['enabled']:
        return

    prefixed_message = f"<{datetime.now()}> [ERROR] {message}\n"

    if error:
        prefixed_message += "\n".join(
            format_exception(type(error), error, error.__traceback__)
        )
    else:
        prefixed_message += "\n".join(format_stack())

    if logging_config['dump_debug_on_error']:
        to_dump = debug_messages[-logging_config['dump_debug_count']:]
        prefixed_message += "\n -- START OF DEBUG DUMP -- "
        for debug_message in to_dump:
            prefixed_message += f"\n{debug_message}"
        prefixed_message += "\n -- END OF DEBUG DUMP -- "

    print(prefixed_message, file=sys.stderr)

    if logging_config['use_file']:
        with open(logging_config['path'], 'a', encoding='UTF-8') as logfile:
            logfile.write(f"{prefixed_message}\n")
