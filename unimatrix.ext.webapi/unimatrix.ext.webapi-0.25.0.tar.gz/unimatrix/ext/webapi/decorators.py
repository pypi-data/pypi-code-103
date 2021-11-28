"""Declares decorator functions to use with :mod:`unimatrix.ext.webapi`."""
import functools

from unimatrix.lib.datastructures import ImmutableDTO


def action(*args, **params):
    """Mark a request handler as a subresource."""
    params.setdefault('detail', False)

    def decorator_factory(func):
        @functools.wraps(func)
        async def decorator(*args, **kwargs):
            return await func(*args, **kwargs)
        decorator.action = ImmutableDTO.fromdict({
            'name': params.get('name') or func.__name__,
            'path': str.replace(func.__name__, '_', '-'),
            'methods': ['GET'],
            **params
        })
        return decorator

    # The decorator is used without any arguments.
    if args and callable(args[0]):
        return decorator_factory(args[0])

    return decorator_factory
