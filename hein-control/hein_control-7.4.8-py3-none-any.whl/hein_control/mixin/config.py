import copy
from functools import wraps
from typing import Callable, Iterable


def _update_args(original_args: tuple,
                 new_args: tuple,
                 ) -> tuple:
    """
    Updates the original argument tuple with the new arguments.

    :param original_args: original argument tuple
    :param new_args: new argument tuple
    :return: updated argument tuple
    """
    original_args = list(original_args)
    for ind, val in enumerate(new_args):
        try:
            original_args[ind] = val
        except IndexError:
            original_args.append(val)
    return tuple(original_args)


def is_builtin_type(obj):
    """returns whether the object is a builtin type"""
    return obj.__class__.__module__ == 'builtins'


def _update_kwargs(original_kwargs: dict,
                   new_kwargs: dict,
                   ) -> dict:
    """
    Updates the original kwargs with the new kwargs. Prevents mutation of the original kwargs.

    Only perform deepcopy on builtin types and interface instances that have specified the deepcopy method.

    :param original_kwargs: original keyword arguments
    :param new_kwargs: new keyword arguments
    :return: consolidated and updated keyword arguments
    """
    # todo compare provided types with signature types
    # create deepcopies of supporting types
    dct = {
        key: copy.deepcopy(value)
        for key, value in original_kwargs.items()
        if hasattr(value, '__deepcopy__') or is_builtin_type(value)
    }
    # add direct references for non-copyable types
    dct.update({
        key: original_kwargs[key] for key in original_kwargs.keys() - dct.keys()
    })
    # finally update with new kwargs
    dct.update(new_kwargs)
    return dct


class Configuration:
    def __init__(self,
                 *args,
                 **kwargs,
                 ):
        """
        Class for storing a configuration for a function execution.

        :param args: arguments
        :param kwargs: keyword arguments
        """
        self._freeze = False
        self._args = args
        self._kwargs = kwargs
        # todo
        #   - update config from ConfiguredAction
        #   - consider moving to basic and leveraging this for Action
        #   - create uuid for each configuration, link configured action to configuration by uuid

    @property
    def _kwarg_string(self) -> str:
        """kwarg representation string"""
        return ", ".join([f"{key}={val}" for key, val in self._kwargs.items()])

    @property
    def _arg_string(self) -> str:
        """arg representation string"""
        return ", ".join([str(arg) for arg in self._args])

    def __repr__(self):
        strings = []
        args = self._arg_string
        if args != '':
            strings.append(args)
        kw = self._kwarg_string
        if kw != '':
            strings.append(kw)
        return f'{self.__class__.__name__}({", ".join(strings)})'

    def __str__(self):
        return self.__repr__()

    def __copy__(self):
        return self.__class__(
            *self._args,
            **self._kwargs,
        )

    def _ensure_unfrozen(fn: Callable):
        """decorator which will do the thing you want"""
        @wraps(fn)
        def decorated(self: 'Configuration', *args, **kwargs):
            if self._freeze is True:
                raise ValueError(f'the instance is frozen and setting or updating of the args or kwargs is disabled')
            return fn(self, *args, **kwargs)
        return decorated

    @_ensure_unfrozen
    def update_args(self, *args):
        """Updates the arguments for the Action"""
        self.args = _update_args(
            self._args,
            args
        )

    @_ensure_unfrozen
    def update_kwargs(self, **kwargs):
        """updates the keyword arguments for the Action"""
        self.kwargs = _update_kwargs(
            self._kwargs,
            kwargs
        )

    @property
    def args(self) -> tuple:
        """arguments for the action"""
        return self._args

    @args.setter
    @_ensure_unfrozen
    def args(self, value: Iterable):
        self._args = value

    @property
    def kwargs(self) -> dict:
        """keyword arguments for the action"""
        return self._kwargs

    @kwargs.setter
    @_ensure_unfrozen
    def kwargs(self, value: dict):
        self._kwargs = value

    @property
    def freeze(self) -> bool:
        """freezes setting or updating of args and kwargs for the instance"""
        return self._freeze

    @freeze.setter
    def freeze(self, value: bool):
        self._freeze = value

    _ensure_unfrozen = staticmethod(_ensure_unfrozen)
