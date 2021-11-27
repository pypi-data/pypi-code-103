import jax.numpy as np
import numpy as onp
import jax

from crikit.covering import Covering, register_covering
from crikit.covering.ufl import get_numpy_shape
from crikit.cr.types import PointMap, Space
from crikit.cr.ufl import UFLExprSpace, UFLFunctionSpace
from crikit.cr.quadrature import get_quadrature_params, make_quadrature_spaces
from crikit.fe import *
from crikit.fe_adjoint import *
from crikit.projection import project
from pyadjoint_utils.jax_adjoint import array, ndarray
from pyadjoint_utils.fenics_adjoint import function_get_local, function_set_local
from pyadjoint_utils import ReducedFunctionNumPy, ReducedFunction
from pyadjoint.tape import (
    no_annotations,
    annotate_tape,
    get_working_tape,
    stop_annotating,
)
from pyadjoint.enlisting import Enlist
from pyadjoint_utils.convert import make_convert_block
from pyadjoint.overloaded_function import overload_function


class JAXArrays(Space):
    """
    See Ndarrays in crikit/cr/numpy.py

    Args:
       shape (Iterable): the shape of the arrays
       dtype (jax.numpy.dtype): the data type (default None)
    """

    def __init__(self, shape, dtype=None):
        self._shape = tuple(shape)
        self._dtype = dtype
        self._indefinite_axes = np.array(shape) < 0
        self._definite_axes = np.logical_not(self._indefinite_axes)
        self._definite_shape = np.asarray(shape)[self._definite_axes]

    @property
    def shape(self):
        return self._shape

    def shape(self):
        return self._shape

    def is_point(self, point):
        if not isinstance(
            point, (np.ndarray, jax.interpreters.xla.DeviceArray, ndarray)
        ):
            return False
        if len(point.shape) != len(self._shape):
            return False
        if self._dtype is not None and self._dtype != point.dtype:
            return False
        return np.array_equal(
            np.asarray(point.shape)[self._definite_axes], self._definite_shape
        )

    def point(self, **kwargs):
        return np.zeros(self._shape)

    def __eq__(self, other):
        return (
            isinstance(other, JAXArrays)
            and self._shape == other._shape
            and self._dtype == other._dtype
        )

    def __repr__(self):
        if self._dtype is None:
            return f"JAXArrays({self._shape})"
        return f"JAXArrays({self._shape}, dtype={self._dtype})"


class JAX_To_UFLFunctionSpace(PointMap):
    def __init__(
        self, source, target, quad_space=None, quad_params=None, make_block=True
    ):
        if quad_space is None:
            quad_space, quad_params = make_quadrature_spaces(
                target, quad_params=quad_params
            )

        self._quad_space = quad_space
        self._dx = dx(metadata=quad_params)

        if isinstance(target, UFLFunctionSpace):
            self._target_space = target._functionspace
        else:
            self._target_space = quad_space

        if source is None:
            quad_shape = get_numpy_shape(self._quad_space)
            source = JAXArrays(quad_shape)

        super().__init__(source, target)

    def __call__(self, arr, **kwargs):
        q = function_set_local(Function(self._quad_space), arr)
        if self._target_space != self._quad_space:
            q = project(q, self._target_space, dx=self._dx)
        return q


class UFLExprSpace_To_JAX(PointMap):
    """Much like UFLExprSpace_To_Numpy, this class maps a UFL expression into a JAX array. The constructor inputs are the same here, replacing Ndarrays with JAXArrays
    Args:
        source (UFLExprSpace or UFLFunctionSpace): the UFL space to use as input.
        target (JAXArrays, optional): the target space to map to.
        quad_space (optional): the finite-element quadrature space to interpolate to.
        quad_params (dict, optional): parameters for the quadrature space.
        domain (optional): the UFL domain for the quadrature space.
    """

    def __init__(
        self, source, target=None, quad_space=None, quad_params=None, domain=None
    ):
        if quad_space is None:
            quad_space, quad_params = make_quadrature_spaces(
                source, quad_params=quad_params, domain=domain
            )
        self._quad_space = quad_space
        self._dx = dx(metadata=quad_params)

        if target is None:
            quad_shape = get_numpy_shape(self._quad_space)
            target = JAXArrays(quad_shape)

        super().__init__(source, target)

    def __call__(self, expr, **kwargs):
        if expr.ufl_shape != self._quad_space.ufl_element().value_shape():
            raise ValueError(
                f"Expression shape {expr.ufl_shape} does not match the target shape of {self._quad_space.ufl_element().value_shape()}"
            )
        if isinstance(expr, Function) and self._quad_space == expr.function_space():
            func = expr
        else:
            func = project(expr, self._quad_space, dx=self._dx)
        res = function_get_local(func)
        return convert_numpy_to_jax(res)


def backend_convert_numpy_to_jax(x):
    return np.array(x)


def backend_convert_jax_to_numpy(x):
    return onp.array(x)


ConvertNumpyToJAX = make_convert_block(
    backend_convert_numpy_to_jax, backend_convert_jax_to_numpy, "ConvertNumpyToJAX"
)
ConvertJAXToNumpy = make_convert_block(
    backend_convert_jax_to_numpy, backend_convert_numpy_to_jax, "ConvertJAXToNumpy"
)

convert_numpy_to_jax = overload_function(
    backend_convert_numpy_to_jax, ConvertNumpyToJAX
)
convert_jax_to_numpy = overload_function(
    backend_convert_jax_to_numpy, ConvertJAXToNumpy
)


@register_covering(UFLExprSpace, JAXArrays)
@register_covering(UFLFunctionSpace, JAXArrays)
class JAX_UFLFunctionSpace_Covering(Covering):
    def __init__(
        self, base_space, covering_space=None, domain=None, quad_params=None, **kwargs
    ):
        quad_space, quad_params = make_quadrature_spaces(
            base_space, quad_params=quad_params, domain=domain
        )
        self._quad_space = quad_space
        self._quad_params = quad_params

        if covering_space is None:
            quad_shape = get_numpy_shape(self._quad_space)
            covering_space = JAXArrays(quad_shape)

        super().__init__(base_space, covering_space, **kwargs)

    def covering_map(self):
        return JAX_To_UFLFunctionSpace(
            self._covering_space,
            self._base_space,
            quad_space=self._quad_space,
            quad_params=self._quad_params,
        )

    def section_map(self):
        return UFLExprSpace_To_JAX(
            self._base_space,
            self._covering_space,
            quad_space=self._quad_space,
            quad_params=self._quad_params,
        )


class ReducedFunctionJAX(ReducedFunctionNumPy):
    """This class implements the ReducedFunction for a given ReducedFunction
    and controls with JAX data structures. Like a ReducedFunctionNumPy, these
    are created from ReducedFunction instances like
    >>> from pyadjoint_utils import overload_jax
    >>> f = overload_jax(lambda x: np.sum(x ** 2))
    >>> x = array(np.array([1.0,2.0]))
    >>> rf = ReducedFunction(f(x),Control(x))
    >>> rf_jax = ReducedFunctionJAX(rf)
    >>> float(rf_jax(x))
    5.0
    """

    def __init__(self, rf):
        if not isinstance(rf, ReducedFunction):
            raise TypeError(
                f"Must pass a ReducedFunction to the ReducedFunctionJAX constructor, not a {type(rf)}!"
            )

        self.rf = rf

    def __call__(self, val):
        ip = self.get_rf_input(array(val))
        output = self.rf(ip)
        return output

    def get_global(self, controls):
        ctrls = []
        for i, val in enumerate(controls):
            if isinstance(val, Control):
                ctrls += val.fetch_numpy(val.control)
            elif hasattr(val, "_ad_to_list"):
                ctrls += val._ad_to_list(val)
            else:
                ctrls += self.controls[i].control._ad_to_list(val)

        return ndarray(np.array(ctrls))

    @no_annotations
    def jac_action(self, val):
        ip = self.get_rf_input(val)
        dJdp = self.rf.jac_action(ip)
        return self.get_outputs_array(dJdp)

    def get_outputs_array(self, vals):
        outs = []
        vals = Enlist(vals)
        for i, out in enumerate(self.outputs):
            if vals[i] is not None:
                outs += out.output._ad_to_list(vals[i])
            else:
                outs += [0] * out.output._ad_dim()

        return ndarray(np.array(outs))
