from typing import NamedTuple, Callable, Any


class Dependency(NamedTuple):
    klass_or_func: Callable[[Any], Any]
    is_singleton: bool = False


def Depends(klass_or_func=None) -> Dependency:
    return Dependency(klass_or_func)


def Singleton(klass_or_func) -> Dependency:
    return Dependency(klass_or_func, True)


def get_indentification(dep: Dependency, *args, **kwargs) -> int:
    """Get idenetification from object and its arguments

    Parameters
    ----------
    dep : Dependency
        Dependency object

    Returns
    -------
    int
        hash value
    """
    key = '.'.join([
        dep.klass_or_func.__module__,
        dep.klass_or_func.__name__
    ])
    hash_value = hash(key)
    for arg in args:
        try:
            hash_value ^= hash(arg)
        except TypeError:
            pass
    for key in sorted(kwargs.keys()):
        try:
            hash_value ^= hash(key) ^ hash(kwargs[key])
        except TypeError:
            pass
    return hash_value
