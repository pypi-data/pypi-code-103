import numpy as np
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()
try:
    from tensorflow.python.ops.parallel_for.gradients import jacobian as tf_jacobian
    from tensorflow.python.ops.parallel_for.gradients import (
        batch_jacobian as tf_batch_jacobian,
    )
except ImportError:
    tf_jacobian = None
    tf_batch_jacobian = None

from pyadjoint.enlisting import Enlist
from pyadjoint.tape import (
    get_working_tape,
    set_working_tape,
    stop_annotating,
    annotate_tape,
)
from pyadjoint.block import Block
from pyadjoint.overloaded_type import create_overloaded_object, register_overloaded_type
from pyadjoint_utils.tensorflow_adjoint import *
from numpy_adjoint import *
from pyadjoint_utils import *
from pyadjoint_utils.numpy_adjoint import *


def get_params_feed_dict(sess=None, variables=None):
    if sess is None:
        sess = tf.get_default_session()
    if variables is None:
        variables = tf.trainable_variables()
    np_variables = sess.run(variables)

    # Convert all trainable_variables to Control-able values.
    overloaded_variables = [create_overloaded_object(v) for v in np_variables]
    feed_dict = dict(zip(variables, overloaded_variables))
    return feed_dict


def backend_run_tensorflow_graph(
    g_outputs,
    feed_dict,
    inputs_conversion=None,
    outputs_conversion=None,
    return_shapes=True,
):
    """This creates a TensorFlow session that runs the graph to generate the desired
    outputs, using the inputs given in the feed dictionary.

    args:
        graph (tensorflow Graph): a tensorflow graph.
        g_outputs (tensorflow tensors): the outputs that should be evaluated
        feed_dict (dictionary): a dictionary mapping the input tensorflow tensor variables to actual values at which
            the outputs should be evaluated.
    """
    if inputs_conversion is None:
        inputs_conversion = convert_feed_dict

    feed_dict = inputs_conversion(feed_dict.copy())
    input_shapes = [np.array(input_value).shape for _, input_value in feed_dict.items()]

    for g_i, val in list(feed_dict.items()):
        if isinstance(g_i, tf.Variable):
            del feed_dict[g_i]
            g_i.load(val)

    sess = tf.get_default_session()
    outputs = sess.run(g_outputs, feed_dict=feed_dict)
    output_shapes = [o.shape for o in outputs] if return_shapes else None

    if outputs_conversion is not None:
        outputs = outputs_conversion(outputs)
    if return_shapes:
        return outputs, (input_shapes, output_shapes)
    return outputs


def convert_feed_dict(feed_dict):
    for g_input, input_value in feed_dict.items():
        if isinstance(input_value, np.ndarray):
            continue
        if not hasattr(input_value, "_ad_to_list"):
            input_value = create_overloaded_object(input_value)
        val = np.array(input_value._ad_to_list(input_value))

        # Get into the right shape.
        shape = g_input.get_shape()
        if shape.rank is not None and shape.dims is not None:
            np_shape = tuple(-1 if s is None else s for s in shape.as_list())
            val = val.reshape(np_shape)
        elif len(val) == 1:
            val = val[0]

        feed_dict[g_input] = val

    return feed_dict


def run_tensorflow_graph(g_outputs, feed_dict, **kwargs):
    annotate = annotate_tape(kwargs)

    block_kwargs = RunTensorFlowGraphBlock.pop_kwargs(kwargs)
    if annotate:
        tape = get_working_tape()
        block_kwargs.update(kwargs)
        block = RunTensorFlowGraphBlock(g_outputs, feed_dict, **block_kwargs)
        tape.add_block(block)

    with stop_annotating():
        g_outputs = Enlist(g_outputs)
        outputs, shapes = backend_run_tensorflow_graph(g_outputs, feed_dict, **kwargs)

    outputs = [create_overloaded_object(o) for o in outputs]

    if annotate:
        for output in outputs:
            block.add_output(output.create_block_variable())
        block.shapes = shapes

    return g_outputs.delist(outputs)


class RunTensorFlowGraphBlock(Block):
    pop_kwargs_keys = ["adj_inputs_conversion", "adj_outputs_conversion", "pointwise"]

    def __init__(self, outputs, feed_dict, **kwargs):
        super(RunTensorFlowGraphBlock, self).__init__()
        self.session = tf.get_default_session()
        self.graph = self.session.graph

        self.adj_inputs_conversion = kwargs.pop("adj_inputs_conversion", None)
        if self.adj_inputs_conversion is None:
            self.adj_inputs_conversion = lambda adj_inputs: map(np.array, adj_inputs)

        self.adj_outputs_conversion = kwargs.pop("adj_outputs_conversion", None)
        if self.adj_outputs_conversion is None:
            self.adj_outputs_conversion = lambda x: x

        self.outputs = Enlist(outputs)
        self.dtype = self.outputs[0].dtype

        self.feed_dict = feed_dict.copy()

        self.inputs = []
        for g_input, input_value in self.feed_dict.items():
            self.add_dependency(input_value)
            self.inputs.append(g_input)

        input_idx = {g_input: i for i, g_input in enumerate(self.inputs)}

        self.pointwise_inputs = kwargs.pop("pointwise", ())
        self.not_pointwise_inputs = [
            g_input for g_input in self.inputs if g_input not in self.pointwise_inputs
        ]
        self.pointwise_idx = [input_idx[g_input] for g_input in self.pointwise_inputs]
        self.not_pointwise_idx = [
            input_idx[g_input] for g_input in self.not_pointwise_inputs
        ]

        self.backward_kwargs = kwargs.copy()
        self.backward_kwargs["outputs_conversion"] = None

        self.forward_kwargs = kwargs.copy()
        self.tlm_args = {"inputs_conversion": kwargs.get("inputs_conversion", None)}

        self.shapes = None
        self.tf_grads = None
        self.tf_jacs = [None] * len(self.outputs)
        self.tf_batch_jacs = [None] * len(self.outputs)

    def __str__(self):
        return "RunTensorFlowGraphBlock"

    def _convert_to_tensors(self, vals):
        with self.graph.as_default():
            tensors = []
            for val in vals:
                tensors.append(tf.convert_to_tensor(val, dtype=self.dtype))
        return tensors

    def _set_feed_dict(self, inputs=None):
        if inputs is None:
            inputs = [bv.saved_output for bv in self.get_dependencies()]
        for input_val, g_input in zip(inputs, self.inputs):
            self.feed_dict[g_input] = input_val

    def _get_jacobian(self, output_idx):
        with self.graph.as_default():
            if self.tf_jacs[output_idx] is None:
                self.tf_jacs[output_idx] = tf_jacobian(
                    self.outputs[output_idx], self.not_pointwise_inputs
                )
            if self.tf_batch_jacs[output_idx] is None:
                self.tf_batch_jacs[output_idx] = list(
                    tf_batch_jacobian(self.outputs[output_idx], g_input)
                    for g_input in self.pointwise_inputs
                )

        with self.session.as_default():
            outs = (self.tf_jacs[output_idx], self.tf_batch_jacs[output_idx])
            full_jacs, batch_jacs = backend_run_tensorflow_graph(
                outs, self.feed_dict, **self.tlm_args, return_shapes=False
            )
        return full_jacs, batch_jacs

    def recompute(self):
        self._set_feed_dict()
        with self.session.as_default():
            outputs, self.shapes = backend_run_tensorflow_graph(
                self.outputs, self.feed_dict, **self.forward_kwargs
            )
        for bv, output in zip(self.get_outputs(), outputs):
            bv.checkpoint = output

    def prepare_evaluate_adj(self, inputs, adj_inputs, relevant_dependencies):
        adj_inputs_np = self.adj_inputs_conversion(adj_inputs)
        if self.tf_grads is None:
            with self.graph.as_default():
                self.adj_inputs_tensors = self._convert_to_tensors(adj_inputs_np)
                self.tf_grads = tf.gradients(
                    self.outputs, self.inputs, grad_ys=self.adj_inputs_tensors
                )
        feed_dict = self.feed_dict.copy()
        for g_i, input_value in zip(self.adj_inputs_tensors, adj_inputs_np):
            feed_dict[g_i] = input_value
        with self.session.as_default():
            grads, _ = backend_run_tensorflow_graph(
                self.tf_grads, feed_dict, **self.backward_kwargs
            )
            grads_dict = self.adj_outputs_conversion(dict(zip(self.inputs, grads)))
            grads = [grads_dict[g_i] for g_i in self.inputs]
        return grads

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]

    def prepare_evaluate_tlm(self, inputs, tlm_inputs, relevant_outputs):
        if tf_jacobian is None:
            raise ValueError(
                "Unable to calculate tlm because couldn't import tensorflow.python.ops.parallel_for.gradients.jacobian"
            )
        self._set_feed_dict(inputs)

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        full_jacs, batch_jacs = self._get_jacobian(idx)
        num_jacs = len(full_jacs) + len(batch_jacs)
        assert num_jacs == len(self.shapes[0]), "%d != %d" % (
            num_jacs,
            len(self.shapes[0]),
        )
        assert num_jacs == len(tlm_inputs), "%d != %d" % (num_jacs, len(tlm_inputs))

        # Do matrix-vector product with tlm_inputs.
        rv = None
        for df_dyi, input_idx in zip(full_jacs, self.not_pointwise_idx):
            input_shape = self.shapes[0][input_idx]
            tlm_input = tlm_inputs[input_idx]
            if tlm_input is None:
                continue
            if hasattr(tlm_input, "vector"):
                tlm_in_mat = tlm_input.vector()[:]
                tlm_in_mat = tlm_in_mat.reshape((-1, *tlm_input.ufl_shape))
            else:
                tlm_in_mat = tlm_input
            dot = np.tensordot(df_dyi, tlm_in_mat, axes=len(input_shape))
            if rv is None:
                rv = dot
            else:
                rv += dot

        output_shape = self.shapes[1][idx]
        for df_dyi, input_idx in zip(batch_jacs, self.pointwise_idx):
            input_shape = self.shapes[0][input_idx]
            tlm_input = tlm_inputs[input_idx]
            if tlm_input is None:
                continue
            if hasattr(tlm_input, "vector"):
                tlm_in_mat = tlm_input.vector()[:]
                tlm_in_mat = tlm_in_mat.reshape((-1, *tlm_input.ufl_shape))
            else:
                tlm_in_mat = tlm_input
            point_rank = len(input_shape) - 1
            w = (
                np.tensordot(a, b, axes=point_rank) for a, b in zip(df_dyi, tlm_in_mat)
            )
            dot = np.zeros(output_shape)
            for k, dotk in enumerate(w):
                dot[k, ...] = dotk
            if rv is None:
                rv = dot
            else:
                rv += dot
        return rv

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        if tf_jacobian is None:
            raise ValueError(
                "Unable to calculate tlm because couldn't import tensorflow.python.ops.parallel_for.gradients.jacobian"
            )
        self._set_feed_dict(inputs)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        # Let f be this block's output and y be this block's inputs. I've calculated the partial
        # derivative jac = df/dy. But the goal is to calculate the derivative wrt x (the controls).
        # Luckily, tlm_inputs is the full derivative dy/dx. So I just need to multiply dy/dx by
        # df/dy to get df/dx.

        # tlm_inputs is a list of the form [dy_1/dx, dy_2/dx, ...]
        #   where dy_i/dx is a list in the form [dy_i/dx_1, dy_i/dx_2, ...]
        #   where dy_i/dx_j is a numpy array.
        # jac is [df/dy_1, df_dy_2, ...].
        # rv = sum_i(tensordot(df/dy_i,dy_i/dx)), where the tensor dot contracts
        #   across the input axes of y_i.

        for tlm_input in tlm_inputs:
            if tlm_input is not None:
                num_controls = len(tlm_input)
                break
        else:
            return None

        full_jacs, batch_jacs = self._get_jacobian(idx)
        num_jacs = len(full_jacs) + len(batch_jacs)

        assert num_jacs == len(self.shapes[0]), "%d != %d" % (
            num_jacs,
            len(self.shapes[0]),
        )
        assert num_jacs == len(tlm_inputs), "%d != %d" % (num_jacs, len(tlm_inputs))

        rv = [None] * num_controls
        for df_dyi, idx in zip(full_jacs, self.not_pointwise_idx):
            input_shape = self.shapes[0][idx]
            dyi_dx = tlm_inputs[idx]
            if dyi_dx is None:
                continue
            for j in range(num_controls):
                if dyi_dx[j] is None:
                    continue
                if isinstance(dyi_dx[j], JacobianIdentity):
                    dot = df_dyi
                else:
                    if hasattr(dyi_dx[j], "shape"):
                        tlm_in_mat = dyi_dx[j]
                    elif hasattr(dyi_dx[j], "vector"):
                        tlm_in_mat = dyi_dx[j].vector()[:]
                    elif hasattr(dyi_dx[j], "values"):
                        tlm_in_mat = dyi_dx[j].values()
                    else:
                        raise NotImplementedError(
                            "Can only handle ndarray, Constant, Function inputs"
                        )

                    dot = np.tensordot(df_dyi, tlm_in_mat, axes=len(input_shape))

                if rv[j] is None:
                    rv[j] = dot
                else:
                    rv[j] += dot

        for df_dyi, idx in zip(batch_jacs, self.pointwise_idx):
            input_shape = self.shapes[0][idx]
            dyi_dx = tlm_inputs[idx]
            if dyi_dx is None:
                continue
            for j in range(num_controls):
                if dyi_dx[j] is None:
                    continue
                if isinstance(dyi_dx[j], JacobianIdentity):
                    dot = df_dyi
                else:
                    if hasattr(dyi_dx[j], "shape"):
                        tlm_in_mat = dyi_dx[j]
                    elif hasattr(dyi_dx[j], "vector"):
                        tlm_in_mat = dyi_dx[j].vector()[:]
                    elif hasattr(dyi_dx[j], "values"):
                        tlm_in_mat = dyi_dx[j].values()
                    else:
                        raise NotImplementedError(
                            "Can only handle ndarray, Constant, Function inputs"
                        )

                    if hasattr(dyi_dx[j], "tlm_shape"):
                        tlm_in_mat = tlm_in_mat.reshape(-1, *dyi_dx[j].tlm_shape)
                    # In the general case, this should probably be a np.tensor dot,
                    # but I'll get to that later, as needed.
                    dot = np.matmul(df_dyi, tlm_in_mat)
                    dot = create_overloaded_object(dot)
                    dot.tlm_shape = dot.shape[1:]

                if rv[j] is None:
                    rv[j] = dot
                else:
                    rv[j] += dot
        return rv
