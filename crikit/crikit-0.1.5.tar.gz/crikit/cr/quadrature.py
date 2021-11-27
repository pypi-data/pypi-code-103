from pyadjoint.enlisting import Enlist
from ufl import Form
from ufl.algorithms.estimate_degrees import SumDegreeEstimator as origSumDegreeEstimator
from ufl.corealg.map_dag import map_expr_dags
from ufl.integral import Integral
from ..fe import mesh_from_ufl_domain, FunctionSpace, FiniteElement, TensorElement


def get_quadrature_params(quad_params=None, default_degree=1):
    if quad_params is None:
        quad_params = {}
    degree = quad_params.get("quadrature_degree", default_degree)
    scheme = quad_params.get("quadrature_rule", "default")

    quad_params["quadrature_rule"] = scheme
    quad_params["quadrature_degree"] = degree
    quad_params["representation"] = "quadrature"
    return quad_params


def make_quadrature_spaces(spaces, quad_params=None, domain=None):
    # Note: Using these points to estimate the quadrature degree may be almost
    #       useless. They're probably not representative of the degree of the
    #       expressions that will be computed.
    spaces = Enlist(spaces)
    points = [s.point() for s in spaces]
    max_arg_degree = max(tuple(estimate_total_polynomial_degree(p) for p in points))
    quad_params = get_quadrature_params(quad_params, max_arg_degree)

    n = len(spaces)
    quad_spaces = [None] * n
    for i in range(n):
        quad_spaces[i] = make_quadrature_space(
            spaces[i].shape(), quad_params, expr=points[i], domain=domain
        )
    return spaces.delist(tuple(quad_spaces)), quad_params


def make_quadrature_space(shape, quad_params, expr=None, domain=None):
    degree = quad_params["quadrature_degree"]
    scheme = quad_params.get("quadrature_rule", "default")
    domain = domain if domain is not None else expr.ufl_domain()
    if domain is None:
        raise ValueError(
            "You must specify the domain (or an expression on the domain) to create a quadrature space"
        )
    cell = domain.ufl_cell()
    mesh = mesh_from_ufl_domain(domain)

    if shape:
        TE = TensorElement(
            "Quadrature", cell, degree=degree, shape=shape, quad_scheme=scheme
        )
    else:
        TE = FiniteElement("Quadrature", cell, degree=degree, quad_scheme=scheme)
    TV = FunctionSpace(mesh, TE)
    return TV


class SumDegreeEstimator(origSumDegreeEstimator):
    """
    This class is equivalent to the original SumDegreesEstimator class except
    for the addition of the of coefficient_replace_map. This map allows the
    degree of any coefficient to be explicitly specified.

    This class also adds handling for sym. I'm not sure if it's correct, though.
    """

    def __init__(self, default_degree, element_replace_map, coefficient_replace_map):
        origSumDegreeEstimator.__init__(self, default_degree, element_replace_map)
        self.coefficient_replace_map = coefficient_replace_map

    def coefficient(self, v):
        """A form coefficient provides a degree based on the coefficient map,
        or the element map, or the default degree if the element has no degree."""
        v = self.coefficient_replace_map.get(v, v)
        if isinstance(v, int):
            return v
        return super().coefficient(v)

    sym = origSumDegreeEstimator._add_degrees


def estimate_total_polynomial_degree(
    e, default_degree=1, element_replace_map={}, coefficient_replace_map={}
):
    """This is equivalent to the original estimate_total_polynomial_degree
    except it supports the coefficient_replace_map argument so that the degree
    of any coefficient can be explicitly specified."""
    de = SumDegreeEstimator(
        default_degree, element_replace_map, coefficient_replace_map
    )
    if isinstance(e, Form):
        if not e.integrals():
            error("Got form with no integrals!")
        degrees = map_expr_dags(de, [it.integrand() for it in e.integrals()])
    elif isinstance(e, Integral):
        degrees = map_expr_dags(de, [e.integrand()])
    else:
        degrees = map_expr_dags(de, [e])
    degree = max(degrees) if degrees else default_degree
    return degree
