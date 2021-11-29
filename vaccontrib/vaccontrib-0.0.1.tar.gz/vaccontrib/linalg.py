# -*- coding: utf-8 -*-
"""
Linear algebra.
"""

import numpy as np

def get_spectral_radius_and_eigenvector(M):
    """
    Does what it says

    Parameters
    ==========
    M : numpy.ndarray
        Array of square shape

    Returns
    =======
    rho : numpy.float64
        spectral radius
    y : numpy.ndarray
        corresponding eigenvector, normalized such that

        .. math::

            \sum_i y_i = 1
    """

    shape = M.shape
    assert(shape[0]==shape[1])

    rho, y = np.linalg.eig(M)
    rho = np.abs(rho)

    ndx = np.argmax(rho)

    rho = rho[ndx]
    y = np.abs(y[:,ndx])
    y /= sum(y)

    return rho, y

def convert_4d_matrix_to_2d_block(K):
    """Convert a 4D matrix of shape ``M, M, V, V`` to a block matrix of shape ``M*V, M*V``"""
    M, _, V, __ = K.shape
    _K = np.zeros((M*V, M*V))
    for i in range(M):
        for j in range(M):
            _K[i*V:(i+1)*V,j*V:(j+1)*V] = K[i,j,:,:]
    return _K

def convert_2d_block_to_4d_matrix(K,M,V):
    """Convert a 2D block matrix of shape ``M*M, M*V`` to a 4D matrix of shape ``M, V, M, V``"""
    _K = np.zeros((M,M,V,V))
    for i in range(M):
        for j in range(M):
            _K[i,j,:,:] = K[i*V:(i+1)*V,j*V:(j+1)*V]
    return _K

if __name__=="__main__":
    M = np.array([[ 1.0,0.],[0.,2.0]])
    print(get_spectral_radius_and_eigenvector(M))


    M, V = 5, 8
    A = np.arange(M**2*V**2).reshape(M,M,V,V)
    A2d = convert_4d_matrix_to_2d_block(A)
    A2 = convert_2d_block_to_4d_matrix(A2d,M,V)
    assert(np.all(np.isclose(A,A2)))
