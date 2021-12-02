
from functools import wraps
from typing import TypeVar
from finjet.container import Container


def set_global_container(container: Container) -> None:
    """Set global container object

    Returns
    -------
    Container
        Container object
    """
    Container.current = container


def get_global_container() -> Container:
    """get global container object

    Returns
    -------
    Container
        Container object
    """
    return Container.current


T = TypeVar('T')


def inject(func: T) -> T:
    """Decorator function of dependency injection.

    Parameters
    ----------
    func : T
        Any function or class.

    Returns
    -------
    T
        func
    """
    @wraps(func)
    def _(*args, **kwargs):
        container = get_global_container()
        if container is not None:
            return container.inject(func)(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return _
