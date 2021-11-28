"""Includes custom exceptions for the supermodels package."""
from typing import Any
from supermodels.logging import get_logger
from supermodels.util import get_object_identifier


class SupermodelsException(BaseException):
    """Provides a base exception class for the supermodels package."""

    def __init__(self, sender: Any, msg: str, *args) -> None:
        """Creates an instance of the exception."""
        self.log_error(sender, msg)
        super().__init__(msg, *args)

    def log_error(self, sender: Any, msg: str) -> None:
        """Generates an error log message for the exception."""
        log_msg = self.get_log_msg(msg)
        identifier = get_object_identifier(sender)

        logger = get_logger(identifier)
        logger.error(log_msg)

    def get_log_msg(self, msg) -> str:
        """Returns the log message for the error log."""
        name = type(self).__name__
        return f"{name}: {msg}"


class ValidationError(SupermodelsException):
    """Provides a custom validation error class."""

    pass


class ImmutableFieldError(SupermodelsException):
    """Provides a custom frozen field error class."""

    pass
