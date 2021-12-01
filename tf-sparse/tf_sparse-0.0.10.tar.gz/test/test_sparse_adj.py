# coding=utf-8
import os

from scipy.sparse import csr_matrix
import numpy as np

from tf_geometric import SparseAdj

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from tf_sparse import SparseMatrix

import tensorflow as tf



edge_index = [
    [0, 0, 0, 0, 1, 1, 4, 6],
    [0, 2, 4, 6, 2, 3, 6, 8]
]

edge_weight = [1, 1, 1, 1, 1, 1, -1, -2]

class MySparseMatrix(SparseMatrix):
    pass

# edge_index = tf.convert_to_tensor(edge_index)
#
# a = SparseMatrix(edge_index)
# print(a.value)
# with tf.GradientTape() as tape:
#     tape.watch(a.value)
#     y = a * a
#     loss = tf.reduce_sum(y.value)
#
# print(tape.gradient(loss, [a.value]))
# asdfasdf

x = tf.sparse.SparseTensor

a = SparseMatrix(edge_index, edge_weight)

print((a * 0.3).to_dense())
# asdfasdf

print(a)
print("============")
print(a.segment_max(axis=-1))
print("sum: ", tf.reduce_sum(a.segment_max(axis=-1)))
print(tf.reduce_max(a.to_dense(), axis=-1))
print("-----------")


print("======")
print(a.segment_sum(axis=0))
print(tf.reduce_sum(a.to_dense(), axis=0))
print("======")
print(a.segment_min(axis=0))
print(tf.reduce_min(a.to_dense(), axis=0))

print("-----")
print(a.segment_mean(axis=-1, keepdims=True))
print(tf.reduce_mean(a.to_dense(), axis=-1, keepdims=True))

print("softmax ----")
print(a.segment_softmax(axis=-1).to_dense())
# asdfasdf

print(0.4 * a)
# asdfasdf

b = a * 0.3

print(b.to_dense())
print((b * b).to_dense())

print((b * np.random.randn(9, 9)).to_dense())

# asdfasdf

b = MySparseMatrix(edge_index)
c = a @ b
print(c.to_dense())
print(c.__class__)
# asdfadsf

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

print(adj.segment_softmax(axis=-1).to_dense())



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