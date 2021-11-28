"""Main module."""
from functools import wraps
from typing import Any, Dict, Tuple
from inspect import getfullargspec, signature


class ObjectConversionError(Exception):
    pass


class takes:
    def __init__(self, klass, name=None):
        self.klass = klass
        self.name = name

    def __call__(self, func):
        spec = getfullargspec(func)
        if self.name is not None and self.name not in spec.args + spec.kwonlyargs:
            raise ValueError(
                f"Parameter name '{self.name}' not a valid argument "
                "to decorated function."
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = self._replace_object(func, args, kwargs)
            return func(*args, **kwargs)

        # This lets us stack @takes decorators,
        # because @wraps does not entirely preserve the signature.
        wrapper.__signature__ = signature(func)

        return wrapper

    def _replace_object(self, func, args, kwargs) -> Tuple[Tuple, Dict]:
        # First positional argument if we don't have a name
        if self.name is None:
            return (self._convert_object(args[0]),) + args[1:], kwargs
        if self.name in kwargs:
            kwargs[self.name] = self._convert_object(kwargs[self.name])
            return args, kwargs

        spec = getfullargspec(func)
        idx = spec.args.index(self.name)
        try:
            obj = self._convert_object(args[idx])
            args = self._replace_obj_at_index(args, obj, index=idx)
        except IndexError:
            # We get here if the decorated function was called
            # where `name` is set to a position-or-kwarg, or kwarg-only,
            # but the function was called with an incorrect kwarg.
            # Python will do the right thing if we just let it call the
            # decorated function without replacing anything.
            pass

        return args, kwargs

    def _replace_obj_at_index(self, items: Tuple, obj: Any, index: int):
        return items[:index] + (obj,) + items[index + 1 :]

    def _convert_object(self, obj):
        if isinstance(obj, self.klass):
            return obj
        try:
            return self.klass(**obj)
        except Exception as exc:
            raise ObjectConversionError(
                f"Error converting {type(obj)} to {self.klass}: {obj}"
            ) from exc
