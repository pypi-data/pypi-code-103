# -*- coding: utf-8 -*-
"""
Functions to compute next generation matrices, contribution matrices,
and other things surrounding those.
"""

import numpy as np
from vaccontrib.linalg import (
            get_spectral_radius_and_eigenvector,
            convert_4d_matrix_to_2d_block,
        )

def get_next_generation_matrix_from_matrices(R0,gamma, S, N, s, r, a, b):
    """
    Construct a next generation matrix from a bunch of
    matrices defining SIR dynamics in a structured,
    vaccinated population.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    gamma : numpy.ndarray of shape ``M x M``
        contact matrix, Entry ``gamma[i,j]``
        contains the average number
        of contacts an average `j`-individual has towards
        `i`-individuals.
    S : numpy.ndarray of shape ``M x V``
        disease-free state, Entry ``S[m,v]`` contains
        the number of m-group individuals
        that are in vaccination state ``v``.
    N : numpy.ndarray of shape ``M``
        population sizes,
        Entry ``population_size[m]`` contains the
        size of population `m`.
    s : numpy.ndarray of shape ``M x V``
        susceptibility reduction,
        Entry ``susceptibility_reduction[m,v]`` contains the
        relative susceptibility reduction of individuals of
        vaccination status `v` and population group `m`.
    r : numpy.ndarray of shape ``M x V``
        transmissibility reduction,
        Entry ``transmissibility_reduction[m,v]`` contains the
        relative transmissibility reduction of individuals of
    a : numpy.ndarray of shape ``M x V``
        relative infection rate, entry ``relative_infection_rate[m,v]``
        contains the
        infection rate (think: shedding rate) of individuals of
        vaccination status `v` and population group `m` relative
        to some base rate.
    b : numpy.ndarray of shape ``M x V``
        relative recovery rate,
        Entry ``relative_recovery_rate[m,v]`` contains the
        recovery rate of individuals of
        vaccination status `v` and population group `m` relative
        to some base rate.

    Returns
    =======
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.
    """


    assert(N.ndim==1)
    for matrix in [gamma,S,s,r,a,b]:
        assert(matrix.ndim==2)
    assert(np.all(np.isclose(S.sum(axis=1),N)))

    M, _ = gamma.shape
    _, V = S.shape

    a0 = a[:,0]
    b0 = b[:,0]
    s0 = s[:,0]
    r0 = r[:,0]

    K0 = np.diag(1-s0).dot(gamma).dot(np.diag(a0)).dot(np.diag(1-r0)).dot(np.diag(1/b0))
    rho0, _ = get_spectral_radius_and_eigenvector(K0)

    if not hasattr(R0,'__len__'):
        R0 = np.ones(V) * R0
    else:
        R0 = np.array(R0,dtype=np.float64)

    K = 1/rho0 * \
            R0[None,None,None,:] * \
            gamma[:,:,None,None] * \
            (1-s[:,None,:,None]) * \
            (1-r[None,:,None,:]) * \
            S[:,None,:,None] * \
            1 / N[None,:,None,None] * \
            a[None,:,None,:] * \
            1 / b[None,:,None,:]

    return K

def get_homogeneous_next_generation_matrix(R0,v,s,r):
    """
    Construct a next generation matrix for a homogeneous
    population with two vaccination stati (not vaccinated,
    vaccinated).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    v : float
        Fraction of individuals that are vaccinated
    s : float
        Susceptibility reduction of vaccine
    r : float
        transmissibility reduction of vaccine

    Returns
    =======
    C : numpy.ndarray of shape ``2, 2``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay where `w` and `v` can be either
        'vaccinated' or 'not vaccinated'
    """

    if not hasattr(R0,'__len__'):
        _R = np.ones(2) * R0
    else:
        _R = np.array(R0,dtype=np.float64)

    assert(_R.ndim==1)

    _S = 0
    _V = 1

    K = np.zeros((2,2))

    K[_S,_S] = (1-v) * _R[_S]
    K[_S,_V] = (1-v) * (1-r) * _R[_V]
    K[_V,_S] = v * (1-s) * _R[_S]
    K[_V,_V] = v * (1-s) * (1-r) * _R[_V]

    return K

def get_homogeneous_contribution_matrix(R0,v,s,r):
    """
    Construct a contribution matrix for a homogeneous
    population with two vaccination stati (not vaccinated,
    vaccinated).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    v : float
        Fraction of individuals that are vaccinated
    s : float
        Susceptibility reduction of vaccine
    r : float
        transmissibility reduction of vaccine

    Returns
    =======
    C : numpy.ndarray of shape ``2, 2``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay where `w` and `v` can be either
        'vaccinated' or 'not vaccinated'
    """

    if not hasattr(R0,'__len__'):
        _R = np.ones(2) * R0
    else:
        _R = np.array(R0,dtype=np.float64)

    assert(_R.ndim==1)

    _S = 0
    _V = 1

    C = np.zeros((2,2))

    C[_S,_S] = (1-v) * (1-v)/(1-v*s) * _R[_S]
    C[_S,_V] = (1-v) * (v*(1-s)/(1-v*s)) * (1-r) * _R[_V]
    C[_V,_S] = v * (1-v)/(1-v*s) * (1-s) * _R[_S]
    C[_V,_V] = v * ( v*(1-s)/(1-v*s)) * (1-s) * (1-r) * _R[_V]

    return C

def get_homogeneous_eigenvector(v,s):
    """
    Construct a population eigenvector for a homogeneous
    population with two vaccination stati (not vaccinated,
    vaccinated).

    Parameters
    ==========
    v : float
        Fraction of individuals that are vaccinated
    s : float
        Susceptibility reduction of vaccine

    Returns
    =======
    C : numpy.ndarray of shape ``2, 2``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay where `w` and `v` can be either
        'vaccinated' or 'not vaccinated'
    """

    _S = 0
    _V = 1

    y = np.zeros(2)

    y[_S] = (1-v)/(1-v*s)
    y[_V] = v*(1-s)/(1-v*s)

    return y

def get_contribution_matrix(K,return_eigenvector_too=False):
    """
    Compute a contribution matrix from a next generation matrix.

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.
    return_eigenvector_too : boolean, default = False
        If true, return the normalized eigenvector
        corresponding to the spectral radius of `K`, as well

    Returns
    =======
    C : numpy.ndarray of shape ``M, M, V, V``
        The system's contribution matrix.
        Entry ``C[i,j,v,w]`` contains the average number
        of `(j,w)`-induced `(i,v)`-offspring during exponential
        growth / decay.

    optional additional returns
    ===========================
    y : numpy.ndarray of shape ``M, V``
        The system's eigenstate that will be approached
        within a few generations. Entry ``y[i,v]`` contains
        the relative number of `(i,v)`-individuals in this
        population.

    """

    M, _, V, __ = K.shape
    _K = convert_4d_matrix_to_2d_block(K)
    R, y = get_spectral_radius_and_eigenvector(_K)
    y = y.reshape(M,V)

    C = K * y[None,:,None,:]

    if return_eigenvector_too:
        return C, y
    else:
        return C

def get_2d_contribution_matrix(K,return_eigenvector_too=False):
    """
    Get the contribution matrix corresponding to a
    2D next generation matrix.

    Parameters
    ==========
    K : numpy.ndarray of shape ``N, N``
        Next generation matrix.
        Entry ``K[i,j]`` contains the average `i`-offspring
        of a single `j`-individual.
    return_eigenvector_too : boolean, default = False
        If true, return the normalized eigenvector
        corresponding to the spectral radius of `K`, as well

    Returns
    =======
    C : numpy.ndarray of shape ``N, N``
        The system's contribution matrix.
        Entry ``C[i,j]`` contains the average number
        of `j`-induced `i`-offspring during exponential
        growth / decay.

    optional additional returns
    ===========================
    y : numpy.ndarray of shape ``N``
        The system's eigenstate that will be approached
        within a few generations. Entry ``y[i]`` contains
        the relative number of `i`-individuals in this
        population.
    """

    R, y = get_spectral_radius_and_eigenvector(K)

    C = K * y[None,:]

    if return_eigenvector_too:
        return C, y
    else:
        return C


def get_reduced_contribution_matrix(K):
    """
    Get the reduced contribution matrix of a covid variant
    (where populations were summed out and only
    vaccination stati remain).

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    C : numpy.ndarray of shape ``V, V``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay.
    """
    C = get_contribution_matrix(K)
    C = C.sum(axis=0).sum(axis=0)
    return C

def get_reduced_vaccinated_susceptible_contribution_matrix(K):
    """
    Get the reduced contribution matrix of a covid variant
    where populations were summed over and active vaccination
    statuses where summed over, as well, such that only vaccinated/
    not vaccinated remains.

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    C : numpy.ndarray of shape ``2, 2``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay where `w` and `v` can be either
        'vaccinated' or 'not vaccinated'
    """
    C = get_reduced_contribution_matrix(K)
    _C = np.zeros((2,2))
    _C[0,0] = C[0,0]
    _C[0,1] = C[0,1:].sum()
    _C[1,0] = C[1:,0].sum()
    _C[1,1] = C[1:,1:].sum()
    return _C

def get_reduced_population_contribution_matrix(K):
    """
    Get the reduced contribution matrix of a covid variant
    (where vaccination stati were summed out and only
    population groups remain).

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    C : numpy.ndarray of shape ``M, M``
        The system's contribution matrix.
        Entry ``C[i,j]`` contains the average number
        of `i`-induced `j`-offspring during exponential
        growth / decay.
    """
    C = get_contribution_matrix(K)
    C = C.sum(axis=-1).sum(axis=-1)
    return C

def get_eigenvector(K):
    """
    The system's eigenstate that will be approached within
    a few generations.

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    y : numpy.ndarray of shape ``M, V``
        The system's eigenstate that will be approached
        within a few generations. Entry ``y[i,v]`` contains
        the relative number of `(i,v)`-individuals in the
        total population.
    """
    _, y = get_contribution_matrix(K,return_eigenvector_too=True)
    return y

def get_reduced_vaccinated_susceptible_eigenvector(K):
    """
    The system's eigenstate that will be approached within
    a few generations.

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    y : numpy.ndarray of length``V``
        The system's eigenstate that will be approached
        within a few generations. Entry ``y[v]`` contains
        the relative number of `v`-individuals in the
        total population.
    """
    _, y = get_contribution_matrix(K,return_eigenvector_too=True)
    y = y.sum(axis=0)
    return y

def get_reduced_population_eigenvector(K):
    """
    The system's eigenstate that will be approached within
    a few generations, where vaccination stati where.
    summed over.

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.

    Returns
    =======
    y : numpy.ndarray of shape ``M``
        The system's eigenstate that will be approached
        within a few generations. Entry ``y[i]`` contains
        the relative number of `i`-individuals in the
        total population.
    """
    _, y = get_contribution_matrix(K,return_eigenvector_too=True)
    y = y.sum(axis=-1)
    return y

if __name__=="__main__":

    gamma = np.array([[1.,1.],[1.,1.]])
    S = np.array([[0.4,0.6],[0.4,0.6]])
    N = np.array([1.,1.])
    s = np.array([[0.,1],[0.,1]])
    r = np.array([[0.,0.],[0.,0.]])
    a = np.array([[1.,1.],[1.,1.]])
    b = np.array([[1.,1.],[1.,1.]])

    K = get_next_generation_matrix_from_matrices(4,gamma,S,N,s,r,a,b)
    C = get_contribution_matrix(K)
    #print(get_spectral_radius_and_eigenvector(K.reshape(2*2,2*2)))
    print(C)
    #print(C.reshape((4,4)))
    print(C.sum(axis=0).sum(axis=0))
    print(C.sum())
