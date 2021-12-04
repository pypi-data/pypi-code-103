"""
Provides the following decorator functions for validating
numerical function arguments:

- validate_positive
- validate_in_interval
"""

from .generic import validate


def validate_positive(argument_names: tuple = (), enable_warnings=True):
    """
    Raises an exception if any argument listed in `argument_names`
    is not positive.

    ---
    Usage: In the example below the decorator checks if the argument
    `width` is positive:
    ``` python
    @validate_positive('width')
    def my_func(id, width = 10):
        pass
    ```
    """
    return validate(
        lambda input: input > 0,
        argument_names,
        message="Must be positive.",
        enable_warnings=enable_warnings,
    )


def validate_in_interval(
    argument_names: tuple = (),
    left=0.0,
    right=1.0,
    left_inclusive=True,
    right_inclusive=True,
    enable_warnings=True,
):
    """
    Raises an exception if any argument listed
    in `argument_names` does not belong to the interval defined by:

    - `left`: A number representing the left interval boundary.
    - `right`: A number representing the right interval boundary.
    - `left_inclusive`: Set to `True` to include left boundary.
    - `right_inclusive`: Set to `True` to include right boundary.

    Note: If `left` < `right` the boundaries will be inversed. In this case,
    `left_inclusive` will refer to the (newly assigned) smaller boundary and
    `right_inclusive` will refer to the (newly assigned) larger boundary.

    ---
    Usage: In the example below the decorator checks if the argument
    `width` is in the interval [10, 20], inclusive.
    ``` python
    @validate_in_interval('width', left = 10, right = 20)
    def my_func(id, width = 10):
        pass
    ```
    """
    if left > right:
        left, right = right, left

    left_operator = "<=" if (left_inclusive) else "<"
    right_operator = "<=" if (right_inclusive) else "<"

    def validator(x_input):
        if left_inclusive and x_input == left:
            return True
        if right_inclusive and x_input == right:
            return True

        if left < x_input < right:
            return True
        return False

    return validate(
        validator,
        argument_names,
        message=f"Input must satisfy: {left} {left_operator} "
        + f"'input' {right_operator} {right}.",
        enable_warnings=enable_warnings,
    )
