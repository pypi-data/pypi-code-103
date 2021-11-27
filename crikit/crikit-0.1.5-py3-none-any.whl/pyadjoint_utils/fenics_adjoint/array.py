from pyadjoint.overloaded_function import overload_function

# from pyadjoint.tape import get_working_tape, set_working_tape, stop_annotating, annotate_tape
from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint_utils import Block
import numpy as np
import jax
from jax import numpy as jnp
from fenics_adjoint import backend
from pyadjoint_utils.numpy_adjoint import *


def backend_function_get_local(f):
    return f.vector().get_local().reshape((-1, *f.ufl_shape))


def backend_function_set_local(f, arr):
    a = np.asarray(arr.flatten())
    f.vector().set_local(a)
    if len(f.vector()) != len(a):
        raise ValueError(
            f"Incorrect array size: {len(f.vector())} != {len(np.asarray(arr.flatten()))}"
        )
    return f


class FunctionGetLocalBlock(Block):
    def __init__(self, f):
        super().__init__()
        self.V = f.function_space()
        self.add_dependency(f)

    def __str__(self):
        return "FunctionGetLocalBlock"

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        f = block_variable.saved_output
        arr = adj_inputs[0]
        adj_value = backend_function_set_local(backend.Function(self.V), arr)
        return adj_value.vector()

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        f = tlm_inputs[0]
        return backend_function_get_local(f)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return tlm_inputs[0]

    def recompute_component(self, inputs, block_variable, idx, prepared):
        f = inputs[0]
        return backend_function_get_local(f)


class FunctionSetLocalBlock(Block):
    def __init__(self, f, arr):
        super().__init__()
        self.V = f.function_space()
        self.add_dependency(arr)

    def __str__(self):
        return "FunctionSetLocalBlock"

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        arr = block_variable.saved_output
        fvec = adj_inputs[0]
        return fvec.get_local().reshape(arr.shape)

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        arr = tlm_inputs[0]
        return function_set_local(backend.Function(self.V), arr)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return tlm_inputs[0]

    def recompute_component(self, inputs, block_variable, idx, prepared):
        arr = inputs[0]
        return backend_function_set_local(backend.Function(self.V), arr)


function_get_local = overload_function(
    backend_function_get_local, FunctionGetLocalBlock
)
function_set_local = overload_function(
    backend_function_set_local, FunctionSetLocalBlock
)
