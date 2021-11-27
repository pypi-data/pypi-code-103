__author__ = "CRIKit Team"
from ._version import __version__

import os

_jax_enable_x64 = os.getenv("JAX_ENABLE_X64")
if _jax_enable_x64 is None or "true" in _jax_enable_x64.lower():
    from jax.config import config as _jax_config

    if not _jax_config.read("jax_enable_x64"):
        _jax_config.update("jax_enable_x64", True)
    del _jax_config

del os

from . import fe
from . import fe_adjoint
from .fe import *
from .fe_adjoint import *
from . import cr
from .cr import (
    CR,
    BlockCR,
    cr_function_shape,
    JAXArrays,
    JAX_To_UFLFunctionSpace,
    UFLExprSpace_To_JAX,
    JAX_UFLFunctionSpace_Covering,
    ReducedFunctionJAX,
    UFLFunctionSpace,
    UFLExprSpace,
    CR_UFL_Expr,
    create_ufl_standins,
    create_ufl_standin_arguments,
    Ndarrays,
    form_get_expr_space,
    assemble_with_cr,
    get_ufl_composite_cr,
    get_cr_form_degree,
    AssembleWithCRBlock,
    Space,
    PointMap,
    DirectSum,
    Callable,
    AugmentPointMap,
    Parametric,
    CompositePointMap,
    ParallelPointMap,
    IdentityPointMap,
)
from . import invariants
from .invariants import (
    symm,
    antisymm,
    eps_ij,
    eps_ijk,
    get_invariant_functions,
    get_invariant_descriptions,
    LeviCivitaType,
    register_invariant_functions,
    InvariantInfo,
    TensorType,
    levi_civita,
)
from . import covering
from .covering import (
    Covering,
    get_composite_cr,
    get_map,
    reset_default_covering_params,
    register_covering,
    get_default_covering_params,
    set_default_covering_params,
    Numpy_UFLFunctionSpace_Covering,
    Numpy_To_UFLFunctionSpace,
    UFLExprSpace_To_Numpy,
    UFLFunctionSpace_UFLExpr_Covering,
    To_UFLFunctionSpace,
    UFLFunctionSpace_UFLFunctionSpace_Covering,
)

from .projection import project, ProjectBlock
from .loss import integral_loss, vector_loss, SlicedWassersteinDistance
from .observer import SurfaceObserver, SubdomainObserver, AdditiveRandomFunction
from . import logging
from .logging import set_log_level
