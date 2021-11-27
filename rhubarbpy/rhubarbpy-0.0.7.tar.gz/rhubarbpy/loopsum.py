from typing import List


from typing import List
from numbers import Number


def loopsum(x: List[Number]) -> Number:
    """A foolish implementation of the sum function
    using a loop in python

    Args:
        x: a list of numbers to sum.
    """
    total = 0.0
    for i in x:
        total += i
    return total


def fibonacci(x: int) -> List[int]:
    """The classic fibonacci function for the
    Nth number in the series.

    Args:
        x: integer value, this returns the xth number
            in the series.
    """
    assert x >= 0

    if x == 0:
        return 0
    elif x <= 2:
        return 1
    else:
        return fibonacci(x - 1) + fibonacci(x - 2)
