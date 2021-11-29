from typing import Callable
from typing import TypeVar


T = TypeVar('T')

class Sanka:

    def __init__(
        self,
        func: Callable,
        callback: Callable[[int], T] = None,
        only_callback_when_dead: bool = True
    ):
        if callback and not callable(callback):
            raise TypeError(f'Callback must be Callable not "{type(callback).__name__}"')

        self.func = func
        self.call_count = 0
        self.callback = callback
        self.only_callback_when_dead = only_callback_when_dead

    def __call__(self, *args, **kwargs):
        if YaDead in args:
            if self.callback and self.only_callback_when_dead:
                self.callback(self.call_count)
            return self.call_count
        else:
            result = self.func(*args, **kwargs)
            self.call_count += 1

            if self.callback and not self.only_callback_when_dead:
                self.callback(self.call_count)

            return result

    def __str__(self):
        return self.func.__name__


def sanka(
    function: Callable = None,
    callback: Callable[[int], T] = None,
    only_callback_when_dead: bool = True
):
    if function:
        return Sanka(function)
    else:
        def wrapper(function):
            return Sanka(function, callback, only_callback_when_dead)
        return wrapper


class YaDead:
    pass

