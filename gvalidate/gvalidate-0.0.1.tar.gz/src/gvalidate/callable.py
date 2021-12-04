"""
Provides the following decorator functions for validating
callable function arguments:

- validate_callable
"""

from .generic import validate


def validate_callable(argument_names: tuple = (), enable_warnings=True):
    """
    Raises an exception if any argument listed in `argument_names`
    is not callable.

    Note: By default all function arguments are validate.

    ---
    Usage: In the example below the decorator checks if the argument
    `callback` is callable:
    ``` python
    @check_callable('callback')
    def my_func(id, callback = lambda x: x*x):
        pass
    ```
    """
    return validate(
        validator=callable,
        argument_names=argument_names,
        message="Must be callable.",
        enable_warnings=enable_warnings,
    )
