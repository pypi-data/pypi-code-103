from .types import PointMap
from .space_builders import DirectSum, enlist
from .numpy import Ndarrays
from .overloaded import overloaded_point_map
from autograd import vector_jacobian_product, jacobian, elementwise_grad
from autograd.numpy.numpy_boxes import ArrayBox
from autograd.numpy.numpy_vspaces import ArrayVSpace
from pyadjoint.enlisting import Enlist
from pyadjoint import AdjFloat
from pyadjoint_utils.numpy_adjoint import ndarray
from pyadjoint_utils.numpy_adjoint.autograd import overload_autograd
from functools import wraps
from itertools import product
import numpy as np
import autograd.numpy as anp

ArrayBox.register(ndarray)
ArrayBox.register(AdjFloat)
ArrayVSpace.register(ndarray)
ArrayVSpace.register(AdjFloat)

from autograd.extend import defvjp


def vjpmaker_trace(ans, x, offset=0, axis1=0, axis2=1):
    axes = tuple(range(x.ndim))
    eye = anp.eye(x.shape[axis1], x.shape[axis2], k=offset, dtype=bool)
    eye = anp.where(eye, anp.ones_like(x), anp.zeros_like(x))

    def vjp(g):
        g = anp.expand_dims(g, axis=axis1)
        g = anp.expand_dims(g, axis=axis2)
        return eye * g

    return vjp


defvjp(anp.trace, vjpmaker_trace)


class AutogradPointMap(PointMap):
    def __init__(self, source, target, func, bare=False, pointwise=True):
        self._orig_func = func
        self._bare = bare

        # Autograd requires once one simple type (ndarray/stdnumeric) per *args index: fit ag_func to that
        if self._bare:
            self._ag_func = self._orig_func
        else:

            @wraps(self._orig_func)
            def _expanded_func(*args, **kwargs):
                return self._orig_func(args, **kwargs)

            self._ag_func = _expanded_func

        self._overloaded_func = overload_autograd(self._ag_func, pointwise)
        self.pointwise = self._overloaded_func.pointwise
        super().__init__(source, target)

    def __repr__(self):
        return f"AutogradPointMap({self._orig_func})"

    def __call__(self, arg, **kwargs):
        if isinstance(self.source, DirectSum):
            return self._overloaded_func(*arg, **kwargs)
        else:
            return self._overloaded_func(arg, **kwargs)


def point_map(source_tuple, target_tuple, **kwargs):
    """This decorator turns the decorated function into an AutogradPointMap.

    The given tuples are used to create :class:`~crikit.cr.numpy.Ndarrays` spaces to set as the
    source and target spaces.
    """
    dtype = kwargs.get("dtype", None)
    if source_tuple is None:
        source = None
    elif any(isinstance(s, tuple) for s in source_tuple):
        source = DirectSum(*tuple(Ndarrays(s, dtype) for s in source_tuple))
    else:
        source = Ndarrays(source_tuple, dtype)
    if any(isinstance(t, tuple) for t in target_tuple):
        target = DirectSum(*tuple(Ndarrays(t, dtype) for t in target_tuple))
    else:
        target = Ndarrays(target_tuple, dtype)

    def point_map_decorator(func):
        ag = AutogradPointMap(source, target, func, **kwargs)
        return ag

    return point_map_decorator
