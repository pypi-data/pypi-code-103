"""This package contains custom Exceptions that are used in this project."""


import inspect
from typing import Any


class NotDefinedError(NotImplementedError):
    """
    Inheritor of built-in `NotImplementedError` exception
    with more detailed message.

    """

    def __init__(self, instance: Any) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        method_name = inspect.stack()[1][0].f_code.co_name
        self.message = (
            f'Define method `{method_name}` '
            f'in class `{instance.__class__.__name__}`.'
        )
        super().__init__(self.message)
