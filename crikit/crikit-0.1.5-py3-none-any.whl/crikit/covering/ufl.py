from crikit.covering import Covering, register_covering
from crikit.cr.numpy import Ndarrays
from crikit.cr.quadrature import get_quadrature_params, make_quadrature_spaces
from crikit.cr.types import PointMap
from crikit.cr.map_builders import CompositePointMap, IdentityPointMap, ParallelPointMap
from crikit.cr.ufl import UFLExprSpace, UFLFunctionSpace

from crikit.fe import *
from crikit.fe_adjoint import *
from crikit.projection import project
from pyadjoint_utils.fenics_adjoint import function_get_local, function_set_local


class Numpy_To_UFLFunctionSpace(PointMap):
    """This class is a point map that maps a NumPy array to a UFL function space.

    The constructor creates a quadrature space for the target space, using the
    given quadrature parameters. The ``__call__`` method sticks the given array
    into the quadrature space and projects it to the target function space.

    """

    def __init__(self, source, target, quad_space=None, quad_params=None):
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
            source = Ndarrays(quad_shape)

        super().__init__(source, target)

    def __call__(self, array):
        Q = self._quad_space
        V = self._target_space
        q = function_set_local(Function(Q), array)
        if V != Q:
            q = project(q, V, dx=self._dx)
        return q


class UFLExprSpace_To_Numpy(PointMap):
    """This class is a point map that maps an expression to a NumPy array.

    The constructor creates a quadrature space for the source space, using the
    given quadrature parameters. The ``__call__`` method projects the input into the
    quadrature space and extracts the values as a NumPy array.

    Args:
        source (UFLExprSpace or UFLFunctionSpace): the UFL space to use as input.
        target (Ndarrays, optional): the target space to map to.
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
            target = Ndarrays(quad_shape)

        super().__init__(source, target)

    def __call__(self, expr):
        Q = self._quad_space
        assert expr.ufl_shape == Q.ufl_element().value_shape()
        if isinstance(expr, Function) and Q == expr.function_space():
            func = expr
        else:
            func = project(expr, Q, dx=self._dx)
        array = function_get_local(func)
        return array


@register_covering(UFLExprSpace, Ndarrays)
@register_covering(UFLFunctionSpace, Ndarrays)
class Numpy_UFLFunctionSpace_Covering(Covering):

    # Base space should be a UFLExprSpace or a UFLFunctionSpace.
    def __init__(
        self,
        base_space,
        covering_space=None,
        domain=None,
        quad_params=None,
        **covering_params
    ):
        quad_space, quad_params = make_quadrature_spaces(
            base_space, quad_params=quad_params, domain=domain
        )
        self._quad_space = quad_space
        self._quad_params = quad_params

        if covering_space is None:
            quad_shape = get_numpy_shape(self._quad_space)
            covering_space = Ndarrays(quad_shape)

        super().__init__(base_space, covering_space, **covering_params)

    def covering_map(self):
        return Numpy_To_UFLFunctionSpace(
            self._covering_space,
            self._base_space,
            quad_space=self._quad_space,
            quad_params=self._quad_params,
        )

    def section_map(self):
        return UFLExprSpace_To_Numpy(
            self._base_space,
            self._covering_space,
            quad_space=self._quad_space,
            quad_params=self._quad_params,
        )


class To_UFLFunctionSpace(PointMap):
    """This class is a point map that projects a UFL expression to a function space.

    The ``__call__`` method projects the input onto the corresponding output
    function space.

    Args:
        source (UFLExprSpace or UFLFunctionSpace): the source space
        target (UFLFunctionSpace): the target space to project

    """

    def __init__(self, source, target):
        self._target_space = target._functionspace

        super().__init__(source, target)

    def __call__(self, expr):
        return project(expr, self._target_space)


@register_covering(UFLExprSpace, UFLFunctionSpace)
class UFLFunctionSpace_UFLExpr_Covering(Covering):
    # Covering space is a UFLFunctionSpace.
    def covering_map(self):
        return IdentityPointMap(self._covering_space, self._base_space)

    def section_map(self):
        return To_UFLFunctionSpace(self._base_space, self._covering_space)


@register_covering(UFLFunctionSpace, UFLFunctionSpace)
class UFLFunctionSpace_UFLFunctionSpace_Covering(Covering):
    def covering_map(self):
        return To_UFLFunctionSpace(self._covering_space, self._base_space)

    def section_map(self):
        return To_UFLFunctionSpace(self._base_space, self._covering_space)


def get_numpy_shape(function_space):
    return (
        Function(function_space)
        .vector()[:]
        .reshape(-1, *function_space.ufl_element().value_shape())
        .shape
    )
