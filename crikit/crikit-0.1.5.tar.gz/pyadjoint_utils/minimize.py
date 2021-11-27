from pyadjoint import minimize as pyadjoint_minimize
from .callback import Callback, FileLoggerCallback, CallbackCombiner
from typing import Sequence, Callable, Union, Optional


class _default:
    pass


def minimize(
    rf,
    method="L-BFGS-B",
    scale=1.0,
    callbacks=_default(),
    **kwargs,
):
    """CRIKit's wrapper around `pyadjoint`'s `minimize` function that
    itself calls `scipy`'s minimization routines. See pyadjoint's
    documentation for information on `kwargs`, which are passed through
    to pyadjoint's `minimize` function.

    :param rf: The functional to optimize
    :type rf: ReducedFunctional
    :param method: The optimization method used, defaults to `'L-BFGS-B'`
    :type method: str
    :param scale: Scale the loss functional by this amount, defaults to `1.0`
    :type scale: float
    :param callbacks: A list or tuple of callback functions or classes
    to combine into one callback, or a single such callback function,
    or None if no callback is desired. Defaults to a
    {class}`FileLoggerCallback` with default arguments
    :type callbacks: Optional[Sequence[Union[Callable, Callback]]]

    """
    if isinstance(callbacks, _default):
        if "callback" in kwargs:
            callbacks = kwargs["callback"]
        else:
            callbacks = FileLoggerCallback(rf=rf)
    if isinstance(callbacks, (list, tuple)):
        callback = CallbackCombiner(callbacks)
    elif callable(callbacks):
        if isinstance(callbacks, FileLoggerCallback):
            # in the default case, make sure the callback has acccess to
            # the rf being minimized. If the user has passed
            # `write_params=False` to its ctor, this will have no effect
            if callbacks.rf is None:
                callbacks.rf = rf
        callback = callbacks
    else:
        callback = callbacks
    kwargs["callback"] = callback

    return pyadjoint_minimize(rf, method=method, scale=scale, **kwargs)
