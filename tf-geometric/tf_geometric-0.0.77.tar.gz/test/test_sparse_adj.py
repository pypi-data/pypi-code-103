# coding=utf-8
import os

from scipy.sparse import csr_matrix
import numpy as np

from tf_geometric import SparseAdj

os.environ["CUDA_VISIBLE_DEVICES"] = "6"

from tf_sparse import SparseMatrix

import tensorflow as tf



edge_index = [
    [0, 0, 0, 0, 0, 1, 1, 4, 6],
    [0, 0, 2, 4, 6, 2, 3, 6, 8]
]

adj = SparseMatrix(edge_index, merge=True)
print(adj.to_dense())
# asdfasdf
# print(adj)
# print("==========")
# print(adj.to_sparse_tensor())
# print(adj.to_dense())

# print(adj @ np.random.randn(9, 100).astype(np.float32))
# print(np.random.randn(100, 9).astype(np.float32) @ adj)
print(tf.convert_to_tensor(np.random.randn(100, 9).astype(np.float32)) @ adj)
# exit(0)


print(adj.to_dense())
print((adj @ adj).to_dense())

print("scipy")

m = csr_matrix(adj.to_dense().numpy())

print(m.todense())
print((m @ m).todense())

a = (adj @ adj).to_dense()
b = (m @ m).todense()

print("diff")
print(a.numpy() - b)

print(adj.softmax(axis=-1).to_dense())



# print("1 ======")
# print(adj.to_dense())
# print("2 ======")
# print((adj - adj).eliminate_zeros().to_dense())
# print("3 ======")
# print((adj - adj.transpose()).to_dense())
#
# c = (adj - adj).eliminate_zeros()
# print(c)

# print(adj.reduce_sum(axis=-1, keepdims=True))
# h = np.random.randn(9, 20).astype(np.float32)
#
# print(adj @ h)
# print(adj.softmax(axis=-1))

# adj = SparseAdj(adj.index, adj.value, adj.shape)

# print(adj.softmax(axis=-1))