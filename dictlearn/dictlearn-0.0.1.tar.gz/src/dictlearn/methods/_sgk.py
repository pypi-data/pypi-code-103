import numpy as np

from ._omp import omp_postreg, ker_omp_postreg
from ._atom import (_update_atom, _update_patom,
                    _update_atom_ker, _update_patom_ker)


def _sgk_update_atom(F, D, X, atom_index, atom_usages, params):
    d = ((F @ X[atom_index, atom_usages].T) /
         (X[atom_index, atom_usages] @ X[atom_index, atom_usages].T))
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    return d, X[atom_index, atom_usages]


def _sgk_coh_update_atom(F, D, X, atom_index, atom_usages, params):
    sel = [True] * D.shape[1]
    sel[atom_index] = False

    d = (F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         D[:, sel] @ D[:, sel].T @ D[:, atom_index])
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm

    return d, X[atom_index, atom_usages]


def _ker_sgk_update_atom(F, K, A, X, atom_index, atom_usages, params):
    a = F @ X[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    return a, X[atom_index, atom_usages]


def _ker_sgk_coh_update_atom(F, K, A, X, atom_index, atom_usages, params):
    sel = [True] * A.shape[1]
    sel[atom_index] = False

    a = (K @ F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         K @ A[:, sel] @ A[:, sel].T @ K @ A[:, atom_index])
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)

    return a, X[atom_index, atom_usages]


def sgk(Y, D, X, params):
    '''
    Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _sgk_update_atom)
    return D, X


def sgk_reg(Y, D, X, params):
    '''
    Regularized Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_atom(Y, D, X, params, _sgk_update_atom)
    return D, X


def sgk_coh(Y, D, X, params):
    '''
    Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _sgk_coh_update_atom)
    return D, X


def psgk(Y, D, X, params):
    '''
    Parallel Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _sgk_update_atom)
    return D, X


def psgk_reg(Y, D, X, params):
    '''
    Parallel Regularized Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params.regmu)

    D, X = _update_patom(Y, D, X, params, _sgk_update_atom)
    return D, X


def psgk_coh(Y, D, X, params):
    '''
    Parallel Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _sgk_coh_update_atom)
    return D, X


def ker_sgk(K, A, X, params):
    '''
    Kernel Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_sgk_update_atom)
    return A, X


def ker_sgk_reg(K, A, X, params):
    '''
    Regularized Kernel Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params['regmu'])

    A, X = _update_atom_ker(K, A, X, params, _ker_sgk_update_atom)
    return A, X


def ker_sgk_coh(K, A, X, params):
    '''
    Kernel Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_sgk_coh_update_atom)
    return A, X


def ker_psgk(K, A, X, params):
    '''
    Parallel Kernel Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_sgk_update_atom)
    return A, X


def ker_psgk_reg(K, A, X, params):
    '''
    Parallel Regularized Kernel Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params['regmu'])

    A, X = _update_patom_ker(K, A, X, params, _ker_sgk_update_atom)
    return A, X


def ker_psgk_coh(K, A, X, params):
    '''
    Parallel Kernel Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_sgk_coh_update_atom)
    return A, X
