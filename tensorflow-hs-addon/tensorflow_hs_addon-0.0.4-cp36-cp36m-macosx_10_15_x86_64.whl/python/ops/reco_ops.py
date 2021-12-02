
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import load_library
from tensorflow.python.platform import resource_loader
from tensorflow.python.framework import ops


lib_path = resource_loader.get_path_to_datafile('_reco_ops.so')
reco_ops = load_library.load_op_library(lib_path)

group_by_slots = reco_ops.group_by_slots
split_ragged_block = reco_ops.split_ragged_block

pooling_by_slots = reco_ops.pooling_by_slots
pooling_by_slots_grad = reco_ops.pooling_by_slots_grad

get_slot_fids = reco_ops.get_slot_fids


def isin(values, filter):
    return reco_ops.tfhs_is_in(values, filter)


@ops.RegisterGradient("PoolingBySlots")
def _feature_pooling_grad(op, pooled_grad, *unused):
    fid_indices, fid_slots, fid_weights, unique_embeddings, slots = op.inputs
    #print("grad inputs", fid_indices, fid_slots, fid_weights, unique_embeddings, slots)
    #print("grad outputs", op.outputs[0], op.outputs[1])
    #print("pooled grad", pooled_grad)

    grad = pooling_by_slots_grad(
        fid_indices, fid_slots, fid_weights, unique_embeddings, pooled_grad, slots)
    return [None, None, None, grad, None]
