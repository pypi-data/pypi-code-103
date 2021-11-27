from pyadjoint.tape import (
    get_working_tape,
    set_working_tape,
    stop_annotating,
    annotate_tape,
)
from pyadjoint.block import Block
from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint_utils import *
import numpy as np
from fenics import Function, FunctionSpace, MixedElement


def backend_run_network(network, output_space, *args, **kwargs):
    # Each function is reshaped to have value_dimension() columns.
    inputs = []
    for f in args:
        v = np.array(f.vector()).reshape((-1, f.value_dimension(0)))
        inputs.append(v)

    # Concatenate all the input columns together so that each row has all the info for a single point.
    net_in = np.hstack(inputs)

    # Run the network.
    output = network.predict(net_in, **kwargs)

    # TODO: I'm assuming there's only one output for now.
    # Turn the network output into a Function in Q.
    func = Function(output_space)

    func.vector()[:] = output.flatten()

    return func


def run_network(network, output_space, *args, **kwargs):
    annotate = annotate_tape(kwargs)

    if annotate:
        tape = get_working_tape()
        network = create_overloaded_object(network)
        block = RunNetworkBlock(network, output_space, *args, **kwargs)
        tape.add_block(block)

    with stop_annotating():
        output = backend_run_network(network, output_space, *args, **kwargs)

    output = create_overloaded_object(output)

    if annotate:
        block.add_output(output.create_block_variable())

    return output


def get_num_network_inputs_outputs(output_space, *args):
    num_inputs = 0
    for f in args:
        if isinstance(f, Function):
            num_inputs += f.value_dimension(0)
        else:
            num_inputs += f.element().value_dimension(0)

    num_outputs = output_space.element().value_dimension(0)

    return num_inputs, num_outputs


class RunNetworkBlock(Block):
    def __init__(self, network, output_space, *args, **kwargs):
        super(RunNetworkBlock, self).__init__()
        self.add_dependency(network)
        for f in args:
            self.add_dependency(f)
        self.kwargs = kwargs
        self.output_space = output_space

    def __str__(self):
        return "RunNetworkBlock"

    def prepare_evaluate_adj(self, inputs, adj_inputs, relevant_dependencies):
        adj_input = adj_inputs[0]
        net = inputs[0]

        # Assume the network has only one output.
        # Get output into the right shape (column vector).
        output_shape = self.output_space.ufl_element().value_shape()
        if len(output_shape) == 0:
            output_shape = (1,)
        adj_input = np.array(adj_input).reshape((-1, *output_shape))

        net.derivative_calculations(adj_input, debug=False)

        return net.input_err

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        if idx == 0:
            net = block_variable.saved_output
            return net.create_copy(weights=net.param_err)

        # This is the idx-th function.
        func = block_variable.saved_output
        Q = func.function_space()

        # Grab the columns corresponding to this function.
        start = 0
        for i in range(1, idx):
            start += inputs[i].value_dimension(0)
        adj_output = prepared[:, start : start + inputs[idx].value_dimension(0)]

        # The adj_output should be in the same FunctionSpace as the corresponding input.
        q = Function(Q)
        q.vector()[:] = adj_output.flatten()
        return q.vector()

    def prepare_evaluate_tlm(self, inputs, tlm_inputs, relevant_outputs):
        net = inputs[0]
        net.jacobian_calculations()
        return (net.jacobian, net.p_jacobian)

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        net_jacobian, net_p_jacobian = prepared

        # Grab the columns corresponding to each function and multiply by the tlm_input for that function
        start = 0
        rv = None
        for i, tlm_input in enumerate(tlm_inputs):
            if tlm_input is None:
                continue
            if i == 0:
                df_dyi = net_p_jacobian
                if tlm_input is not None and df_dyi is None:
                    raise NotImplementedError(
                        "Jacobian calculations are not complete for %s"
                        % inputs[0].__class__.__name__
                    )
            else:
                # Extract the entries related to this input function.
                df_dyi = net_jacobian[:, start : start + inputs[i].value_dimension(0)]

            if isinstance(tlm_input, JacobianIdentity):
                dot = df_dyi
            else:
                # First, get tlm_input into a numpy array of the right shape.
                if hasattr(tlm_input, "vector"):
                    tlm_in_mat = tlm_input.vector()[:]
                elif hasattr(tlm_input, "values"):
                    tlm_in_mat = tlm_input.values()
                else:
                    raise NotImplementedError(
                        "Can only handle Constant and Function inputs"
                    )

                shape = list(tlm_input.ufl_shape)
                while len(shape) < 2:
                    shape.append(1)
                tlm_in_mat = tlm_in_mat.reshape(-1, *shape)

                # Now do the multication. In the general case, this should probably be a np.tensor dot,
                # but I'll get to that later, as needed.
                dot = np.matmul(df_dyi, tlm_in_mat)

            if rv is None:
                rv = dot
            else:
                rv += dot

            if i != 0:
                start += inputs[i].value_dimension(0)

        if rv is None:
            return
        r = Function(self.output_space)
        r.vector()[:] = rv.flatten()
        return r

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        net = inputs[0]
        net.jacobian_calculations()
        return (net.jacobian, net.p_jacobian)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        net_jacobian, net_p_jacobian = prepared

        for tlm_input in tlm_inputs:
            if tlm_input is not None:
                num_controls = len(tlm_input)
                break
        else:
            return None
        rv = [None] * num_controls

        # Grab the columns corresponding to each function and multiply by the tlm_input for that function
        output_shape = self.output_space.ufl_element().value_shape()
        start = 0
        for i, dyi_dx in enumerate(tlm_inputs):
            if dyi_dx is None:
                continue
            if i == 0:
                df_dyi = net_p_jacobian
                if dyi_dx is not None and df_dyi is None:
                    raise NotImplementedError(
                        "Jacobian calculations are not complete for %s"
                        % inputs[0].__class__.__name__
                    )
            else:
                # Extract the entries related to this input function.
                df_dyi = net_jacobian[:, start : start + inputs[i].value_dimension(0)]
            for j in range(num_controls):
                if dyi_dx[j] is None:
                    continue
                # Now I need to multiply df_dyi by dyi_dx[j].

                # First, get dyi_dx[j] into a numpy array of the right shape.
                if hasattr(dyi_dx[j], "vector"):
                    tlm_in_mat = dyi_dx[j].vector()[:]
                elif hasattr(dyi_dx[j], "values"):
                    tlm_in_mat = dyi_dx[j].values()
                else:
                    raise NotImplementedError(
                        "Can only handle Constant and Function inputs"
                    )
                tlm_in_mat = tlm_in_mat.reshape(-1, *dyi_dx[j].tlm_shape)

                # Now do the multication. In the general case, this should probably be a np.tensor dot,
                # but I'll get to that later, as needed.
                output = np.matmul(df_dyi, tlm_in_mat)

                if rv[j] is None:
                    rv[j] = output
                else:
                    rv[j] += output

            if i != 0:
                start += inputs[i].value_dimension(0)

        for j, tlm_output in enumerate(rv):
            if tlm_output is None:
                continue
            # I'm representing the Jacobian as a MixedElement where each mixed element consists of the
            # output element repeated multiple times.
            output_shape_indices = len(self.output_space.ufl_element().value_shape())
            tlm_shape = tlm_output.shape[1:]
            derivative_size = np.prod(tlm_shape[output_shape_indices:])

            Telem = MixedElement([self.output_space.ufl_element()] * derivative_size)
            T = FunctionSpace(self.output_space.mesh(), Telem)

            t = Function(T)
            t.vector()[:] = tlm_output.flatten()
            t.tlm_shape = tlm_shape

            rv[j] = t
        return rv

    def recompute(self):
        deps = self.get_dependencies()
        net = deps[0].saved_output
        args = [bv.saved_output for bv in deps[1:]]
        output = backend_run_network(net, self.output_space, *args, **self.kwargs)
        self.get_outputs()[0].checkpoint = output
