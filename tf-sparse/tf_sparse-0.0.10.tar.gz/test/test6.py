# coding=utf-8
import os

# from scipy.sparse import csr_matrix
# import numpy as np
#
# from tf_geometric import SparseAdj

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# from tf_sparse import SparseMatrix
import tensorflow as tf

import tensorflow as tf

print(tf.shape(tf.random.truncated_normal([3, 5])))
asdfasdf

#
# class A(object):
#     is_tensor_like = True
#     pass
#
# class B(A):
#     pass
#
# print(tf.is_tensor(tf.sparse.eye(5)))
# asdfasdf
#
# tf.sparse.SparseTensor
#
# edge_index = [
#     [0, 0, 0, 0, 1, 1, 4, 6],
#     [0, 2, 4, 6, 2, 3, 6, 8]
# ]
#
# edge_weight = [1, 1, 1, 1, 1, 1, -1, -2]
#
# class MySparseMatrix(SparseMatrix):
#     pass
#
#
#
# x = tf.random.truncated_normal([4, 5])
#
#
# # print(tf.convert_to_tensor(x.shape))
# # asdfasdf
#
#
# # print(type(x.shape), x.shape)
# # print(type(tf.shape(x)), tf.shape(x))
# # print(type(x.shape[0]), x.shape[0])
# # print(type(tf.shape(x)[0]), tf.shape(x)[0])
# # print("===========")
# # print(type(len(x)), len(x))
# # asdfadsf
#
#
# a = SparseMatrix(edge_index, edge_weight)
#
# print(type(len(a)))
# # sdafsadf
#
# tf.shape
#
# tf.sparse.SparseTensor
#
#
# @tf.function
# def test():
#     return a * tf.convert_to_tensor(3.0)
#
# print(test())