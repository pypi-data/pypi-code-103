"""
Includes the following *generic* decorator functions:

- validate

"""

from functools import wraps
from inspect import signature
from typing import Tuple, Union
from warnings import warn


def validate(
    validator: callable,
    argument_names: Union[Tuple[str], str] = (),
    message: str = "",
    error_type: type = ValueError,
    enable_warnings=True,
) -> None:
    """
    Generic validator function that raises an exception if any positional
    arguments specified by an integer in the tuple `argument_names`
    or any keyword arguments
    specified by a string are not valid.

    - validator: A function that must return `False` if the argument is
      invalid.
    - argument_names: A tuple containing the names of
      all arguments that need to be validated or a string.
    - message: Optional string that will be appended to the error message.
    - error_type: Optional parameter used to specify the type of error raised.
    - enable_warnings: Set to `True` to generate a warning if any entry
      of `argument_names` is not a valid argument name.

    Note: Skips arguments that are absent (since an error will be
    thrown implicitly when the decorated function is called.)

    If the user supplied validator function raises an exception,
    validation will fail and relevant information is appended
    to the error message before raising the error using a `from` construct.

    ---
    Usage: In the example below the decorator checks if the argument
    `width` is larger than zero.

    ``` python
    @validate(
        validator=lambda input: input > 0,
        argument_names = ('width',),
        message='Must be larger than zero.',
    )
    def my_func(length, width):
    pass

    my_func(10, -2)

    #Stacktrace will be printed ...
    ValueError: Invalid argument: width = -2. Must be larger than zero.
    ```
    """
    if isinstance(argument_names, str):
        argument_names = (argument_names,)

    def _validate(func):
        @wraps(func)
        def __validate(*args, **kwargs):
            # Map args onto kwargs:
            all_argument_names = tuple(signature(func).parameters.keys())
            mapped_kwargs = kwargs.copy()
            for index, arg_value in enumerate(args):
                mapped_kwargs[all_argument_names[index]] = arg_value

            def _argument_validation(current, arg_name: str):
                """
                Calls the validator, generates info, raises exception
                on validation failure.
                """
                validation_error = None
                try:
                    valid = validator(current)
                    info = (
                        f"Invalid argument in function {func.__name__}: "
                        + f"{arg_name} = {current}."
                    )
                    if not valid:
                        # Exception raised after validation failed.
                        validation_error = error_type(
                            info + " " + str(message)
                        )
                        raise validation_error
                except Exception as error:
                    # Check if exception was raised already
                    if error == validation_error:
                        raise
                    # Attach message and raise again.
                    info = (
                        "Exception raised while validating argument in "
                        + f"{func.__name__}: {arg_name} = {current}."
                    )
                    error.args = (info + " " + str(message), *error.args)
                    raise error_type from error

            # Validate all entries if argument_names is empty.
            if not argument_names:
                for arg_name in mapped_kwargs.keys():
                    current = mapped_kwargs[arg_name]
                    _argument_validation(current, arg_name)

            # Validation
            for arg_name in argument_names:
                if arg_name in mapped_kwargs:
                    current = mapped_kwargs[arg_name]
                    _argument_validation(current, arg_name)
                else:
                    if enable_warnings:
                        warn(
                            "Warning: {} is not a valid argument name. "
                            "Check the decorators of {}.".format(
                                arg_name, func.__name__
                            )
                        )

            return func(*args, **kwargs)

        return __validate

    return _validate
