# coding=utf-8
import os
import tensorflow as tf
from tf_geometric.utils import tf_utils

import tf_geometric as tfg
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class A():

    def __init__(self, edge_index):
        self.edge_index = edge_index

    @property
    def num_edges(self):
        shape = tf.shape(self.edge_index)
        if shape[0] == 0:
            return 10
        else:
            return 6

@tf_utils.function
def test(x, edge_index):
    # a = A(edge_index)
    # return a.num_edges()
    # return tf.shape(edge_index)[0] == 0
    graph = tfg.Graph(x, edge_index)
    return graph.num_edges


x = tf.random.truncated_normal([10, 5])
edge_index = tf.convert_to_tensor([
    [0, 1, 3, 5],
    [0, 2, 4, 5]
])

print(test(x, edge_index))