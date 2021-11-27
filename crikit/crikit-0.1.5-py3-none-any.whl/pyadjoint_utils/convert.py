from pyadjoint.overloaded_function import overload_function

from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint_utils import Block
from fenics_adjoint import backend
import numpy as np
from jax import numpy as jnp
from pyadjoint_utils.numpy_adjoint import *


class ConvertXToYBlock(Block):
    def __init__(self, x):
        super().__init__()
        self.name = "ConvertXToYBlock"
        self.add_dependency(x)

    def __str__(self):
        return self.name

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        y_adj = adj_inputs[0]
        return self.backend_convert_y_to_x(y_adj)

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        x_tlm = tlm_inputs[0]
        return self.backend_convert_x_to_y(x_tlm)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return tlm_inputs[0]

    def recompute_component(self, inputs, block_variable, idx, prepared):
        x = inputs[0]
        return self.backend_convert_x_to_y(x)

    def evaluate_hessian_component(
        self,
        inputs,
        hessian_inputs,
        adj_inputs,
        block_variable,
        idx,
        relevant_dependencies,
        prepared=None,
    ):
        y_hess = hessian_inputs[0]
        return self.backend_convert_y_to_x(y_hess)


def make_convert_block(convert_x_to_y, convert_y_to_x, name):
    class ConvertXToYBlockChild(ConvertXToYBlock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = name
            self.backend_convert_x_to_y = convert_x_to_y
            self.backend_convert_y_to_x = convert_y_to_x

    ConvertXToYBlockChild.__name__ = name
    ConvertXToYBlockChild.__qualname__ = name
    return ConvertXToYBlockChild


from pyadjoint.overloaded_function import overload_function


def backend_convert_numpy_to_float(x):
    return float(x)


def backend_convert_float_to_numpy(x):
    import numpy as np

    return np.array(x)


ConvertNumpyToFloat = make_convert_block(
    backend_convert_numpy_to_float,
    backend_convert_float_to_numpy,
    "ConvertNumpyToFloat",
)
ConvertFloatToNumpy = make_convert_block(
    backend_convert_float_to_numpy,
    backend_convert_numpy_to_float,
    "ConvertFloatToNumpy",
)

convert_numpy_to_float = overload_function(
    backend_convert_numpy_to_float, ConvertNumpyToFloat
)
convert_float_to_numpy = overload_function(
    backend_convert_float_to_numpy, ConvertFloatToNumpy
)
