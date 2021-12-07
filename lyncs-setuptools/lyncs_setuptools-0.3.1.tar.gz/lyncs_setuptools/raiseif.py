"""
A decorator that raises error if condition is satisfied instead of executing the function
"""

from functools import wraps


def raiseif(fail, error):
    "Decorator that raises error if condition is satisfied"

    def decorator(fnc):
        if not fail:
            return fnc

        @wraps(fnc)
        def raiser(*args, **kwargs):
            raise error

        return raiser

    return decorator
