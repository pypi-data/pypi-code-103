from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint.enlisting import Enlist
from pyadjoint import *
from pyadjoint_utils import *
from pyadjoint_utils.tensorflow_adjoint import (
    get_params_feed_dict,
    run_tensorflow_graph,
)
from pyadjoint_utils.fenics_adjoint import function_get_local, function_set_local
from .space_builders import DirectSum
from .types import PointMap
from .numpy import Ndarrays
import numpy as np
from crikit.fe import Function, project, grad


class CRTensorFlow(PointMap):
    def __init__(
        self,
        inputs,
        outputs,
        session,
        input_space=None,
        output_space=None,
        tf_kwargs=None,
    ):
        self.g_inputs = Enlist(inputs)
        self.g_outputs = Enlist(outputs)
        self.tf_kwargs = tf_kwargs if tf_kwargs is not None else {}
        self.session = session
        self.graph = self.session.graph

        with self.graph.as_default():
            self.feed_dict = get_params_feed_dict(self.session)
        self.params_keys = [g_p for g_p in self.feed_dict]
        self.params = [p for g_p, p in self.feed_dict.items()]
        self.params_controls = [Control(p) for p in self.params]

        if input_space is None:
            input_spaces = []
            for t in self.g_inputs:
                shape = tuple(-1 if s.value is None else s.value for s in t.shape)
                # Don't pass the dtype since it can break valid Space conversions.
                # We could fix the problem by adding an NdarrayToNdarray covering that handles dtype stuff.
                # input_spaces.append(Ndarrays(shape, dtype=t.dtype.as_numpy_dtype))
                input_spaces.append(Ndarrays(shape))
            input_space = DirectSum(input_spaces)
            input_space = self.g_inputs.delist(input_space)

        if output_space is None:
            output_spaces = []
            for t in self.g_outputs:
                shape = tuple(-1 if s.value is None else s.value for s in t.shape)
                # output_spaces.append(Ndarrays(shape, dtype=t.dtype.as_numpy_dtype))
                output_spaces.append(Ndarrays(shape))
            output_space = DirectSum(output_spaces)
            output_space = self.g_outputs.delist(output_space)

        super().__init__(input_space, output_space)

    def _set_feed_dict(self, inputs):
        assert len(inputs) == len(self.g_inputs), "%d != %d" % (
            len(inputs),
            len(self.g_inputs),
        )

        for input_val, g_input in zip(inputs, self.g_inputs):
            self.feed_dict[g_input] = input_val

    def __call__(self, args):
        self.inputs = Enlist(args)
        self._set_feed_dict(self.inputs)
        with self.session.as_default():
            outputs = run_tensorflow_graph(
                self.g_outputs, self.feed_dict, **self.tf_kwargs
            )
            outputs = self.g_outputs.delist(outputs)
        self.controls = [Control(a) for a in self.inputs]
        self.rf = ReducedFunction(outputs, self.controls)
        return outputs

    def numpy_call(self, args):
        args = Enlist(args)
        self._set_feed_dict(args)
        with self.session.as_default():
            outputs = run_tensorflow_graph(
                self.g_outputs, self.feed_dict, annotate=False
            )
            outputs = self.g_outputs.delist(outputs)
        return outputs

    def setParams(self, params):
        self.params = params
        self.params_controls = [Control(p) for p in self.params]

        for g_p, p in zip(self.params_keys, self.params):
            self.feed_dict[g_p] = p
