import numpy as np

from ._omp import omp_postreg, ker_omp_postreg
from ._atom import (_update_atom, _update_patom,
                    _update_atom_ker, _update_patom_ker)


def _uaksvd_update_atom(F, D, X, atom_index, atom_usages, params):
    d = F @ X[atom_index, atom_usages].T
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = ((F - np.outer(D[:, atom_index], X[atom_index, atom_usages])).T @ d +
         X[atom_index, atom_usages])
    return d, x


def _uaksvd_reg_update_atom(F, D, X, atom_index, atom_usages, params):
    d = F @ X[atom_index, atom_usages].T
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = ((F - np.outer(D[:, atom_index], X[atom_index, atom_usages])).T @ d +
         X[atom_index, atom_usages]) / (1 + params['regmu'])
    return d, x


def _uaksvd_coh_update_atom(F, D, X, atom_index, atom_usages, params):
    sel = [True] * D.shape[1]
    sel[atom_index] = False

    d = (F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         D[:, sel] @ D[:, sel].T @ D[:, atom_index])
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm
    x = ((F - np.outer(D[:, atom_index], X[atom_index, atom_usages])).T @ d +
         X[atom_index, atom_usages])
    return d, x


def _ker_uaksvd_update_atom(F, K, A, X, atom_index, atom_usages, params):
    a = F @ X[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = (F - np.outer(A[:, atom_index], X[atom_index, atom_usages]) +
         np.outer(a, X[atom_index, atom_usages])).T @ K @ a
    return a, x


def _ker_uaksvd_reg_update_atom(F, K, A, X, atom_index, atom_usages, params):
    a = F @ X[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = ((F - np.outer(A[:, atom_index], X[atom_index, atom_usages]) +
         np.outer(a, X[atom_index, atom_usages])).T @ K @ a /
         (1 + params['regmu']))
    return a, x


def _ker_uaksvd_coh_update_atom(F, K, A, X, atom_index, atom_usages, params):
    sel = [True] * A.shape[1]
    sel[atom_index] = False

    a = (K @ F @ X[atom_index, atom_usages].T - 2 * params['gamma'] *
         K @ A[:, sel] @ A[:, sel].T @ K @ A[:, atom_index])
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)
    x = (F - np.outer(A[:, atom_index], X[atom_index, atom_usages]) +
         np.outer(a, X[atom_index, atom_usages])).T @ K @ a
    return a, x


def uaksvd(Y, D, X, params):
    '''
    Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _uaksvd_update_atom)
    return D, X


def uaksvd_reg(Y, D, X, params):
    '''
    Updated-error Regularized Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_atom(Y, D, X, params, _uaksvd_reg_update_atom)
    return D, X


def uaksvd_coh(Y, D, X, params):
    '''
    Updated-error Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_atom(Y, D, X, params, _uaksvd_coh_update_atom)
    return D, X


def puaksvd(Y, D, X, params):
    '''
    Parallel Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _uaksvd_update_atom)
    return D, X


def puaksvd_reg(Y, D, X, params):
    '''
    Parallel Regularized Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_patom(Y, D, X, params, _uaksvd_reg_update_atom)
    return D, X


def puaksvd_coh(Y, D, X, params):
    '''
    Parallel Updated-error Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    D, X = _update_patom(Y, D, X, params, _uaksvd_coh_update_atom)
    return D, X


def ker_uaksvd(K, A, X, params):
    '''
    Kernel Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_uaksvd_update_atom)
    return A, X


def ker_uaksvd_reg(K, A, X, params):
    '''
    Regularized Kernel Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_uaksvd_reg_update_atom)
    return A, X


def ker_uaksvd_coh(K, A, X, params):
    '''
    Kernel Updated-error Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_uaksvd_coh_update_atom)
    return A, X


def ker_puaksvd(K, A, X, params):
    '''
    Parallel Kernel Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_uaksvd_update_atom)
    return A, X


def ker_puaksvd_reg(K, A, X, params):
    '''
    Parallel Kernel Regularized Updated-error Approximate K-SVD.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params['regmu'])

    A, X = _update_patom_ker(K, A, X, params, _ker_uaksvd_reg_update_atom)
    return A, X


def ker_puaksvd_coh(K, A, X, params):
    '''
    Parallel Kernel Updated-error Approximate K-SVD with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_uaksvd_coh_update_atom)
    return A, X
