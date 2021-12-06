"""
Exceptions raised by OS base classes
"""


class CommandError(Exception):
    """
    Exceptions raised by shell commands
    """


class LoggerError(Exception):
    """
    Exceptions raised by logging configuration
    """


class FileParserError(Exception):
    """
    Exceptions raised while parsing text files
    """
