from ..block import Block
from pyadjoint.overloaded_type import OverloadedType
from ..adjfloat import AdjFloat
from pyadjoint.enlisting import Enlist
import jax
import jax.numpy as jnp
from jax.tree_util import Partial as partial


class ArrayOperatorBlock(Block):
    # a simpler JAXBlock that's independent of the actual JAXBlock implementation so as not to create a circular dependency
    def __init__(self, operator, args, output):
        super().__init__()
        self._operator = operator
        self._args = [convert_arg(x) for x in args]
        for dep in args:
            self.add_dependency(dep)

    def recompute_component(self, inputs, block_variable, idx, prepared):
        return self._operator(*(convert_arg(x) for x in inputs))


class AddBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return adj_inputs[0]

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        x_dot, y_dot = (convert_arg(val) for val in tlm_inputs)
        return sum([x if x is not None else 0 for x in [x_dot, y_dot]])

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
        return hessian_inputs[0]


class SubBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        if idx == 0:
            return adj_inputs[0]
        return -adj_inputs[0]

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        x_dot, y_dot = (convert_arg(val) for val in tlm_inputs)
        output = 0
        if x_dot is not None:
            output = output + x_dot
        if y_dot is not None:
            output = output - y_dot

        return output


class MulBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        other_idx = 0 if idx == 1 else 1
        return self._operator(
            convert_arg(adj_inputs[0]), convert_arg(inputs[other_idx])
        )

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        x_dot, y_dot = (convert_arg(val) for val in tlm_inputs)
        output = 0
        if x_dot is not None:
            output = output + self._operator(convert_arg(inputs[1]), x_dot)
        if y_dot is not None:
            output = output + self._operator(convert_arg(inputs[0]), y_dot)
        return output


@jax.jit
def _compiled_pow(x, y):
    # for use in DivBlock
    return x ** y


class DivBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        z_bar = convert_arg(adj_inputs[0])
        if idx == 0:
            return z_bar / convert_arg(inputs[1])
        else:
            return (
                -z_bar
                * convert_arg(inputs[0])
                / _compiled_pow(convert_arg(inputs[1]), 2)
            )

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):

        x, y = (convert_arg(val) for val in inputs)
        x_dot, y_dot = (convert_arg(val) for val in tlm_inputs)

        @jax.jit
        def _tlm_arg_0(x, y, x_dot):
            return x_dot / y

        @jax.jit
        def _tlm_arg_1(x, y, y_dot):
            return -y_dot * (x / (y ** 2))

        tlm = []

        if x_dot is not None:
            tlm.append(_tlm_arg_0(x, y, x_dot))
        if y_dot is not None:
            tlm.append(_tlm_arg_1(x, y, y_dot))

        return sum(tlm)


class NegBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return -convert_arg(adj_inputs[0])

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return -convert_arg(tlm_inputs[0])


class PowBlock(ArrayOperatorBlock):
    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        x, y = (convert_arg(val) for val in inputs)
        z_bar = convert_arg(adj_inputs[0])

        @jax.jit
        def _arg_0_vjp(x, y, z_bar):
            # vjp w.r.t. x; derivative is y * x ** (y - 1)
            return z_bar * y * (x ** (y - 1))

        @jax.jit
        def _arg_1_vjp(x, y, z_bar):
            # vjp w.r.t. y; derivative is log(x) * x ** y
            return z_bar * jnp.log(x) * (x ** y)

        if idx == 0:
            return _arg_0_vjp(x, y, z_bar)
        else:
            return _arg_1_vjp(x, y, z_bar)

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):

        x, y = (convert_arg(val) for val in inputs)
        x_dot, y_dot = (convert_arg(val) for val in tlm_inputs)

        @jax.jit
        def _tlm_arg_0(x, y, x_dot):
            return x_dot * y * (x ** (y - 1))

        @jax.jit
        def _tlm_arg_1(x, y, y_dot):
            return y_dot * jnp.log(x) * (x ** y)

        tlm = []

        if x_dot is not None:
            tlm.append(_tlm_arg_0(x, y, x_dot))
        if y_dot is not None:
            tlm.append(_tlm_arg_1(x, y, y_dot))
        return sum(tlm)


def convert_arg(x):
    if not isinstance(x, OverloadedType):
        return x

    if hasattr(x, "value"):
        return x.value
    elif hasattr(x, "saved_output"):
        return convert_arg(x.saved_output)
    else:
        return x  # see if it works! (it probably won't, and you'll get an exception from a function higher up the call chain)
