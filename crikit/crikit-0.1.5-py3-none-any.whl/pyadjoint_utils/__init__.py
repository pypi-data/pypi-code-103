from pyadjoint import *
from pyadjoint.enlisting import Enlist
from .adjfloat import AdjFloat
from .block import Block
from .block_variable import BlockVariable
from .identity import JacobianIdentity, make_jacobian_identities
from .tape import Tape, push_tape
from .reduced_function import ReducedFunction
from .reduced_function_numpy import ReducedFunctionNumPy
from .drivers import (
    compute_gradient,
    compute_jacobian_action,
    compute_jacobian_matrix,
    compute_hessian_action,
)
from .control import Control
from .solving.equation import ReducedEquation
from .solving.snes_solver import SNESSolver
from .verification import taylor_test, taylor_to_dict
from .tape_block import record_tape_block
from .minimize import minimize
from .callback import Callback, FileLoggerCallback, CallbackCombiner

try:
    from .numpy_adjoint import overload_autograd
except:
    pass

try:
    from .tensorflow_adjoint import get_params_feed_dict, run_tensorflow_graph
except:
    pass

from .fenics_adjoint import (
    homogenize_bcs,
    assemble,
    AssembleBlock,
    function_get_local,
    function_set_local,
    backend,
    compat,
)
from .jax_adjoint import (
    ndarray,
    array,
    asarray,
    to_jax,
    to_adjfloat,
    overload_jax,
    set_default_dtype,
    get_default_dtype,
)

# Make sure OverloadedType uses our version of BlockVariable.
from pyadjoint import OverloadedType


def create_block_variable(self):
    self.block_variable = BlockVariable(self)
    return self.block_variable


OverloadedType.create_block_variable = create_block_variable
del create_block_variable

from pyadjoint import set_working_tape

set_working_tape(Tape())
