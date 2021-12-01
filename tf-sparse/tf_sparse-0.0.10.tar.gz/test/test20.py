# coding=utf-8
import os

from tf_geometric import SparseAdj
from tf_geometric.nn import gcn_norm_adj

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import tensorflow as tf
import numpy as np
import time

from tf_sparse import SparseMatrix
from tf_geometric.utils import tf_utils
import tensorflow as tf
import tf_geometric as tfg
from tqdm import tqdm
import time

# x = tf.constant(5.0)


# graph, (train_index, valid_index, test_index) = tfg.datasets.CoraDataset().load_data()

# graph = tfg.Graph(
#     x=np.random.randn(5, 20),  # 5 nodes, 20 features,
#     edge_index=[[0, 0, 1, 3, 2, 1],
#                 [1, 2, 2, 1, 1, 3]],  # 4 undirected edges
#     edge_weight=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
# )

num_nodes = 20

graph = tfg.Graph(
    x=np.random.randn(num_nodes, 20),  # 5 nodes, 20 features,
    edge_index=np.random.randint(0, num_nodes, [2, 10]),  # 4 undirected edges
    # edge_weight=[
)

import tensorflow as tf

# adj = SparseAdj(graph.edge_index, graph.edge_weight, shape=[graph.num_nodes, graph.num_nodes])
# adj.index = tf.constant(adj.index.numpy())
# adj.value = tf.constant(adj.value.numpy())
# # adj.index = adj.index.numpy()
# # adj.value = adj.value.numpy()
#
# y = tf.constant(4.0)

# @tf.function
# def forward(graph):
#     adj = SparseAdj(graph.edge_index, graph.edge_weight, shape=[graph.num_nodes, graph.num_nodes])
#     return adj @ graph.x

adj = SparseAdj(graph.edge_index, graph.edge_weight, shape=[graph.num_nodes, graph.num_nodes])

gcn_norm_adj(adj, cache=graph.cache)

@tf.function
def forward(graph):
    adj_ = gcn_norm_adj(adj, cache=graph.cache)
    return adj_ @ graph.x

# for _ in range(10):
#     print(forward(x))

forward_ = forward.get_concrete_function(graph)
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