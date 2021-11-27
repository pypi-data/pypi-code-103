from ufl import (
    FiniteElement,
    VectorElement,
    TensorElement,
    FunctionSpace,
    Coefficient,
    Argument,
    replace,
    inner,
)
from ufl.algorithms.analysis import extract_coefficients
from ufl.core.expr import Expr
from pyadjoint.enlisting import Enlist

from .types import PointMap, Space
from .space_builders import DirectSum, enlist


class UFLFunctionSpace(Space):
    """Represents a UFL FunctionSpace."""

    def __init__(self, functionspace):
        """
        Args:
            functionspace (ufl.FunctionSpace): the function space to wrap.
        """
        self._functionspace = functionspace

    def shape(self):
        return self._functionspace.ufl_element().value_shape()

    def is_point(self, point):
        return (
            hasattr(point, "ufl_function_space")
            and point.ufl_function_space() == self._functionspace
        )

    def point(self):
        return Coefficient(self._functionspace)

    def __eq__(self, other):
        return (
            isinstance(other, UFLFunctionSpace)
            and self._functionspace == other._functionspace
        )


class UFLExprSpace(Space):
    """Represents a space of UFL expression of a certain shape, defined by an
    example expression. Any UFL expression of the same shape lies in this space.
    """

    def __init__(self, expr, tlm_shape=None, ufl_domains=None):
        """
        Args:
            expr (ufl.core.expr.Expr): a UFL expression defining the space
            tlm_shape (tuple, optional): used to explicitly specify the shape of the space instead
                of getting it from the expression.

        TODO:
            * Rename ``tlm_shape`` arg to just ``shape``.
            * ufl_domains documentation
        """
        self._expr = expr
        self.ufl_shape = tlm_shape if tlm_shape is not None else expr.ufl_shape
        self.ufl_domains = (
            ufl_domains if ufl_domains is not None else expr.ufl_domains()
        )

    def shape(self):
        return self.ufl_shape

    def __repr__(self):
        domain_names = tuple(str(d) for d in self.ufl_domains)
        return f"UFLExprSpace(" + str(domain_names) + f",{self.ufl_shape!s})"

    def is_point(self, point):
        right_shape = isinstance(point, Expr) and point.ufl_shape == self.ufl_shape
        pd = point.ufl_domain()
        in_domain = self.ufl_domains is () or pd is None or (pd in self.ufl_domains)
        return right_shape and in_domain

    def point(self, domain_idx=None):
        """Returns the expression that this space was initialized with."""
        domain = None if domain_idx is None else self.ufl_domains[domain_idx]
        return Coefficient(
            FunctionSpace(domain, TensorElement("Real", shape=self.ufl_shape))
        )

    def __eq__(self, other):
        # I commented out the ufl_domains check since it can break the use case of
        #  converting from a domain-free space to a specific domain space, even though
        #  anything in the former can be in the latter.
        # To support that properly, we either need the idea of super/subspace comparisons
        #  or UFLtoUFL coverings that just use IdentityPointMaps.
        return isinstance(other, UFLExprSpace) and self.ufl_shape == other.ufl_shape
        # and self.ufl_domains == other.ufl_domains


class CR_UFL_Expr(PointMap):

    _abstract_element = FiniteElement("Real")

    def __init__(self, arg_space, exprs, pos_map, domain=None):
        """Take an expression for each component of the CR.

        Provide map for how the expression coefficients map to CR arguments."""

        # TODO: Entuple would be good instead of Enlist.
        self.exprs = Enlist(exprs)
        domains = [e.ufl_domain() for e in self.exprs]
        self.pos_map = pos_map

        ufl_domains = () if domain is None else (domain,)
        out_spaces = tuple(UFLExprSpace(e, ufl_domains=ufl_domains) for e in self.exprs)
        out_space = self.exprs.delist(DirectSum(*out_spaces))
        super(CR_UFL_Expr, self).__init__(arg_space, out_space)

    def __call__(self, args):
        if not isinstance(self.source, DirectSum):
            args = [args]
        self.inputs = args
        arg_map = {}
        out_list = []
        for key in self.pos_map:
            arg_map[key] = self.inputs[self.pos_map[key]]
        for expr in self.exprs:
            out_list.append(replace(expr, arg_map))
        return self.exprs.delist(out_list)

    def update_coefficients(self, replace_map):
        exprs = tuple(map(lambda e: replace(e, replace_map), self.exprs))

        # A hacky way to keep the enlistment the same.
        listed = self.exprs.listed
        self.exprs = Enlist(exprs)
        self.exprs.listed = listed


# Example
class CR_P_Laplacian(CR_UFL_Expr):
    """This CR is applied directly to ufl expressions"""

    def __init__(self, p=2, dim=2, input_u=True, domain=None):

        self._p = p
        self._input_u = input_u
        base_element = CR_UFL_Expr._abstract_element

        g = Coefficient(FunctionSpace(domain, VectorElement(base_element, dim=dim)))
        expr = g * (inner(g, g) + 1e-12) ** ((self._p - 2) / 2.0)

        if self._input_u:
            u = Coefficient(FunctionSpace(domain, base_element))
            arg_space = DirectSum(UFLExprSpace(u), UFLExprSpace(g))
            pos_map = {g: 1}
        else:
            arg_space = UFLExprSpace(g)
            pos_map = {g: 0}

        super(CR_P_Laplacian, self).__init__(arg_space, expr, pos_map)
        self.setParams(self._p)

    def setParams(self, p):
        self.update_coefficients({self._p: p})
        self._p = p
        self.params = self._p


def create_ufl_standins(shapes, domain=None):
    """Create standins for the outputs of a CR that can go in forms"""
    standins = []
    for s in shapes:
        if s:
            standins.append(
                Coefficient(FunctionSpace(domain, TensorElement("Real", shape=s)))
            )
        else:
            standins.append(Coefficient(FunctionSpace(domain, FiniteElement("Real"))))
    return tuple(standins)


def create_ufl_standin_arguments(shapes, number=0, domain=None):
    """Create standins for the outputs of a CR that can go in forms"""
    return tuple(
        Argument(FunctionSpace(domain, TensorElement("Real", shape=s)), number)
        for s in shapes
    )


def point_map(source_tuple, bare=False, domain=None, **kwargs):
    """This decorator turns the decorated function into a :class:`~crikit.cr.ufl.CR_UFL_Expr`.

    The given tuples are used to create :class:`~crikit.cr.ufl.UFLExprSpace` spaces to set as the
    source and target spaces.

    The decorated function will be run once to create the UFL expression for the point map.
    """
    # Get source_tuple in the form of a tuple of shapes.
    if source_tuple is None:
        source_tuple = ()
    elif not any(isinstance(s, tuple) for s in source_tuple):
        source_tuple = (source_tuple,)

    ufl_domains = () if domain is None else (domain,)

    # Generate inputs for the function and build the source space.
    inputs = create_ufl_standins(source_tuple)
    input_dict = {arg: i for i, arg in enumerate(inputs)}
    if len(inputs) == 0:
        source = None
    elif len(inputs) == 1:
        if bare:
            raise ValueError("bare should be False for functions with a single input")
        inputs = inputs[0]
        source = UFLExprSpace(inputs, ufl_domains=ufl_domains)
    else:
        source = DirectSum(
            tuple(UFLExprSpace(e, ufl_domains=ufl_domains) for e in inputs)
        )

    def point_map_decorator(ufl_func):
        outputs = ufl_func(*inputs) if bare else ufl_func(inputs)
        pm = CR_UFL_Expr(source, outputs, input_dict, domain=domain)
        return pm

    return point_map_decorator
