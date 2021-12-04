from collections import Counter
from typing import Callable, Tuple, Any, Iterable
from functools import partial, wraps
from time import perf_counter

def timeit(function: Callable=None, print_time: bool = True, *args) -> Callable:
    """
    Decorator for measuring the runtime of a function.
    Example usage:
    @timeit
    def my_function(x, y, z):
        return np.sqrt(x ** 2 + y ** 2 + z ** 2)
    the new decorated function will then return its
    result and the runtime in a tuple, i.e.
    my_function(1, 1, 0) --> (1.41..., runtime:float)

    By default, also prints a string
    'Ran in {runtime} seconds', this can be disabled
    by passing print_time=False, for example
    @timeit(print_time=False)
    def my_function(x, y, z):
        ...

    This clever syntax of being able to use the decorator
    by itself or with arguments was heavily inspired (basically
    copy pasted) from this StackOverflow answer:
    https://stackoverflow.com/a/60832711/8304249
    """
    assert callable(function) or function is None
    @wraps(function)
    def _decorator(function):
        def wrapper(*args) -> Tuple[Any, float]:
            start = perf_counter()
            result = function(*args)
            end = perf_counter()
            runtime = end - start
            if print_time:
                print(f'Ran in {end - start} seconds')
            return result, runtime
        return wrapper
    return _decorator(function) if callable(function) else _decorator

def most_common(iterable: Iterable[Any]) -> Any:
    """
    Returns the most common element in the given iterable.
    Arguments:
    iterable: Iterable[Any] - The iterable to work on
    """
    return Counter(iterable).most_common()[0][0]

def least_common(iterable: Iterable[Any]) -> Any:
    """
    Returns the least common element in the given iterable.
    Arguments:
    iterable: Iterable[Any] - The iterable to work on
    """
    return Counter(iterable).most_common()[-1][0]
