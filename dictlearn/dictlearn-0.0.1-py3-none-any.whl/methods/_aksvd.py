import numpy as np

from ._omp import omp_postreg, ker_omp_postreg
from ._atom import (_update_atom, _update_patom,
                    _update_atom_ker, _update_patom_ker)


def _aksvd_update_atom(F, D, X, atom_index, atom_usages, params):
    d = F @ X[atom_index, atom_usages].T
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = F.T @ d
    return d, x


def _aksvd_reg_update_atom(F, D, X, atom_index, atom_usages, params):
    d = F @ X[atom_index, atom_usages].T
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = F.T @ d / (1 + params['regmu'])
    return d, x


def _aksvd_coh_update_atom(F, D, X, atom_index, atom_usages, params):
    sel = [True] * D.shape[1]
    sel[atom_index] = False

    d = (F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         D[:, sel] @ D[:, sel].T @ D[:, atom_index])
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = F.T @ d
    return d, x


def _ker_aksvd_update_atom(F, K, A, X, atom_index, atom_usages, params):
    a = F @ X[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = F.T @ K @ a
    return a, x


def _ker_aksvd_reg_update_atom(F, K, A, X, atom_index, atom_usages, params):
    a = F @ X[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = F.T @ K @ a / (1 + params['regmu'])
    return a, x


def _ker_aksvd_coh_update_atom(F, K, A, X, atom_index, atom_usages, params):
    sel = [True] * A.shape[1]
    sel[atom_index] = False

    a = (K @ F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         K @ A[:, sel] @ A[:, sel].T @ K @ A[:, atom_index])
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = F.T @ K @ a
    return a, x


def aksvd(Y, D, X, params):
    '''
    Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _aksvd_update_atom)
    return D, X


def aksvd_reg(Y, D, X, params):
    '''
    Regularized Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_atom(Y, D, X, params, _aksvd_reg_update_atom)
    return D, X


def aksvd_coh(Y, D, X, params):
    '''
    Approximate K-SVD algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _aksvd_coh_update_atom)
    return D, X


def paksvd(Y, D, X, params):
    '''
    Parallel Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _aksvd_update_atom)
    return D, X


def paksvd_reg(Y, D, X, params):
    '''
    Parallel Regularized Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_patom(Y, D, X, params, _aksvd_reg_update_atom)
    return D, X


def paksvd_coh(Y, D, X, params):
    '''
    Parallel Approximate K-SVD algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _aksvd_coh_update_atom)
    return D, X


def ker_aksvd(K, A, X, params):
    '''
    Kernel Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_aksvd_update_atom)
    return A, X


def ker_aksvd_reg(K, A, X, params):
    '''
    Regularized Kernel Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_aksvd_reg_update_atom)
    return A, X


def ker_aksvd_coh(K, A, X, params):
    '''
    Regularized Kernel Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_aksvd_coh_update_atom)
    return A, X


def ker_paksvd(K, A, X, params):
    '''
    Parallel Kernel Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_aksvd_update_atom)
    return A, X


def ker_paksvd_reg(K, A, X, params):
    '''
    Parallel Regularized Kernel approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params['regmu'])

    A, X = _update_patom_ker(K, A, X, params, _ker_aksvd_reg_update_atom)
    return A, X


def ker_paksvd_coh(K, A, X, params):
    '''
    Parallel Kernel Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_aksvd_coh_update_atom)
    return A, X
