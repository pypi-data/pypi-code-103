"""This submodule defines a default FE adjoint backends (FEniCS or Firedrake)"""

from .fe import crikit_fe_backend

if crikit_fe_backend == "firedrake":
    from firedrake_adjoint import *
elif crikit_fe_backend == "fenics":
    from fenics_adjoint import *
else:
    ImportError("Unrecognized adjoint backend")

from pyadjoint_utils import *
