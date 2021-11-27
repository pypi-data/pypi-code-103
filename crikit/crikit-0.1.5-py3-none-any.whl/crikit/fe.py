"""This submodule defines a default FE backend (FEniCS or Firedrake)"""

from ufl import indices, as_tensor

try:
    from firedrake import *

    crikit_fe_backend = "firedrake"
except ModuleNotFoundError:
    try:
        from fenics import *

        crikit_fe_backend = "fenics"
        from ffc.quadrature.deprecation import (
            QuadratureRepresentationDeprecationWarning,
        )
        import warnings

        warnings.simplefilter("ignore", QuadratureRepresentationDeprecationWarning)
        del warnings, QuadratureRepresentationDeprecationWarning
        dx = dx(metadata={"representation": "quadrature"})
    except ModuleNotFoundError:
        raise ImportError("Could not import a FE backend")


def mesh_from_ufl_domain(domain):
    if crikit_fe_backend == "firedrake":
        return domain
    else:
        return domain.ufl_cargo()


def contraction(a, a_axes, b, b_axes):
    "UFL operator: Take the contraction of a and b over given axes."
    ai, bi = a_axes, b_axes
    if len(ai) != len(bi):
        error("Contraction must be over the same number of axes.")
    ash = a.ufl_shape
    bsh = b.ufl_shape
    aii = list(indices(len(a.ufl_shape)))  ######### Convert tuple to list
    bii = list(indices(len(b.ufl_shape)))  ######### Convert tuple to list
    cii = indices(len(ai))
    shape = [None] * len(ai)
    for i, j in enumerate(ai):
        aii[j] = cii[i]
        shape[i] = ash[j]
    for i, j in enumerate(bi):
        bii[j] = cii[i]
        if shape[i] != bsh[j]:
            error("Shape mismatch in contraction.")
    aii = tuple(aii)  ######### Convert list back to tuple
    bii = tuple(bii)  ######### Convert list back to tuple
    s = a[aii] * b[bii]
    cii = set(cii)
    ii = tuple(i for i in (aii + bii) if i not in cii)
    return as_tensor(s, ii)
