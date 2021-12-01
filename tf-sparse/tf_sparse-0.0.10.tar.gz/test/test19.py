# coding=utf-8
import os

from tf_geometric import SparseAdj
from tf_geometric.nn import gcn_norm_adj

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import tensorflow as tf
import numpy as np
import time

from tf_sparse import SparseMatrix



import tensorflow as tf


edge_index = [
    [0, 0, 0, 0, 1, 1, 4, 6],
    [0, 2, 4, 6, 2, 3, 6, 8]
]

edge_weight = [1, 1, 1, 1, 1, 1, -1, -2]

adj = SparseAdj(edge_index, edge_weight, shape=[20, 20])
# print(type(adj))
adj = gcn_norm_adj(adj)
# print(type(adj.index), type(adj2.index))
# asdfasdf
# cache = {}
# gcn_norm_adj(adj, cache=cache)
# key = list(cache.keys())[0]

x = np.random.randn(20, 5).astype(np.float32)
#
# class Data(object):
#     def __init__(self, x, cache):
#         self.x = x
#         self.cache = cache

@tf.function
def forward(x):

    return adj @ x

# for _ in range(10):
#     print(forward(x))

forward_ = forward.get_concrete_function(x)
graph = forward_.graph

with open("other.txt", "w", encoding="utf-8") as f:
    f.write(str(graph.as_graph_def()))
exit(0)

#
# start_time = time.time()
# for i in range(1, 100):
#     forward(x)
#     if i % 10 == 0:
#         end_time = time.time()
#         print((end_time - start_time) / i)