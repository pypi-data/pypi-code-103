"""
Provides the following decorators for validating arguments of type `string`:

- validate_non_whitespace
"""

from .generic import validate


def validate_non_whitespace(argument_names: tuple = (), enable_warnings=True):
    """
    Raises an exception if any string argument listed in `argument_names`
    contains only whitespace.

    ---
    Usage: In the example below the decorator checks if the argument
    `name` contain a non-whitespace string.
    ``` python
    @validate_non_whitespace('name')
    def my_func('month', name = 'Anna'):
        pass
    ```
    """
    return validate(
        lambda input: input.isspace(),
        argument_names,
        message="Input contains non-whitespace characters.",
        enable_warnings=enable_warnings,
    )
