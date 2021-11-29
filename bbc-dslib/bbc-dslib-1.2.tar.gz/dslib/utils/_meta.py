from functools import reduce
from typing import Any, Callable


def resolve(name: str) -> Any:
    """
    Loads a variable, function, class or module from a given dotted path (e.g. 'dslib.utils.resolve').
    Copied directly from: https://github.com/python/cpython/blob/master/Lib/logging/config.py
    :param name: (str) name (or dotted path) of the element to be imported
    :return: loaded class, function or module
    """
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    return found


def _compose_2(f: Callable, g: Callable) -> Callable:
    return lambda *a, **kw: f(g(*a, **kw))


def compose(*functions: Callable) -> Callable:
    """
    Composes functions provided as input and returns the composite function (e.g. compose(f, g, h) will return fogoh)
    :param functions: (func) input functions to be composed
    :return: (func) composite function
    """
    return reduce(_compose_2, functions)
