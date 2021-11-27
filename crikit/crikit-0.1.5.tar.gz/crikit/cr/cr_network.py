from fenics import *
from fenics_adjoint import *
from pyadjoint import *
from pyadjoint_utils import *
from ..network_block import run_network
from .space_builders import DirectSum
from .ufl import UFLFunctionSpace
from .types import PointMap
import numpy as np


def get_total_value_dimension(spaces):
    total = 0
    for V in spaces:
        total += V.element().value_dimension(0)
    return total


class CRNetwork(PointMap):
    def __init__(self, input_spaces, output_space, network):
        self.input_spaces = input_spaces
        self.output_space = output_space

        self.num_inputs = get_total_value_dimension(self.input_spaces)
        self.num_outputs = get_total_value_dimension((self.output_space,))

        # Make sure the network has the right number of inputs and outputs.
        self.setParams([network])
        assert (
            self.network.num_inputs == self.num_inputs
        ), "Network has %d inputs but should have %d" % (
            self.network.num_inputs,
            self.num_inputs,
        )
        assert (
            self.network.num_outputs == self.num_outputs
        ), "Network has %d outputs but should have %d" % (
            self.network.num_outputs,
            self.num_outputs,
        )

        arg_space = DirectSum([UFLFunctionSpace(V) for V in self.input_spaces])
        out_space = UFLFunctionSpace(self.output_space)

        if len(arg_space) == 1:
            arg_space = arg_space[0]

        super().__init__(arg_space, out_space)

    def __call__(self, args):
        if not isinstance(self.source, DirectSum):
            args = [args]
        output = run_network(self.network, self.output_space, *args)

        self.inputs = args
        self.controls = [Control(a) for a in self.inputs]
        self.rf = ReducedFunction(output, self.controls)
        return output

    def numpy_call(self, *inputs):
        net_input = np.concatenate(inputs, axis=1)
        return self.network.predict(net_input)

    def setParams(self, params):
        if not isinstance(params, (list, tuple)):
            params = [params]
        self.network = params[0]
        self.params = [self.network]
        self.params_controls = [Control(self.network)]
