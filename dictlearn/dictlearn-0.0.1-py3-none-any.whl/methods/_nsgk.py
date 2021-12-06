import numpy as np

from ._omp import omp_postreg, ker_omp_postreg
from ._atom import (_update_atom, _update_patom,
                   _update_atom_ker, _update_patom_ker)


def _nsgk_update_atom(F, D, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(D[:, atom_index], X0[atom_index, atom_usages].T))

    d = ((F @ X0[atom_index, atom_usages].T) /
         (X0[atom_index, atom_usages] @ X0[atom_index, atom_usages].T))
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm

    E[:, atom_usages] = F - np.outer(d, X0[atom_index, atom_usages])
    _nsgk_update_atom.E = E

    return d, X0[atom_index, atom_usages]


def _nsgk_coh_update_atom(F, D, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_coh_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(D[:, atom_index], X0[atom_index, atom_usages].T))

    sel = [True] * D.shape[1]
    sel[atom_index] = False

    d = (F @ X0[atom_index, atom_usages].T - 2 * params['gamma'] *
         D[:, sel] @ D[:, sel].T @ D[:, atom_index])
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm

    E[:, atom_usages] = F - np.outer(d, X0[atom_index, atom_usages])
    _nsgk_coh_update_atom.E = E

    return d, X0[atom_index, atom_usages]


def _pnsgk_update_atom(F, D, X0, atom_index, atom_usages, params):
    # update error
    E = _pnsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(D[:, atom_index], X0[atom_index, atom_usages].T))

    d = ((F @ X0[atom_index, atom_usages].T) /
         (X0[atom_index, atom_usages] @ X0[atom_index, atom_usages].T))
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm

    return d, X0[atom_index, atom_usages]


def _pnsgk_coh_update_atom(F, D, X0, atom_index, atom_usages, params):
    # update error
    E = _pnsgk_coh_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(D[:, atom_index], X0[atom_index, atom_usages].T))

    sel = [True] * D.shape[1]
    sel[atom_index] = False

    d = ((F @ X0[atom_index, atom_usages].T - 2 * params['gamma'] *
         D[:, sel] @ D[:, sel].T @ D[:, atom_index]) /
         (X0[atom_index, atom_usages] @ X0[atom_index, atom_usages].T))
    d_norm = np.linalg.norm(d)
    if d_norm >= params['atom_norm_tolerance']:
        d /= d_norm

    return d, X0[atom_index, atom_usages]


def _ker_nsgk_update_atom(F, K, A, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(A[:, atom_index], X0[atom_index, atom_usages].T))

    a = F @ X0[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)

    E[:, atom_usages] = (F - np.outer(a, X0[atom_index, atom_usages]))
    _nsgk_update_atom.E = E

    return a, X0[atom_index, atom_usages]


def _ker_nsgk_coh_update_atom(F, K, A, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(A[:, atom_index], X0[atom_index, atom_usages].T))

    sel = [True] * A.shape[1]
    sel[atom_index] = False

    a = (K @ F @ X0[atom_index, atom_usages].T - 2 * params['gamma'] *
         K @ A[:, sel] @ A[:, sel].T @ K @ A[:, atom_index])
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)

    E[:, atom_usages] = (F - np.outer(a, X0[atom_index, atom_usages]))
    _nsgk_update_atom.E = E

    return a, X0[atom_index, atom_usages]


def _ker_pnsgk_update_atom(F, K, A, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(A[:, atom_index], X0[atom_index, atom_usages].T))

    a = F @ X0[atom_index, atom_usages].T
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)

    return a, X0[atom_index, atom_usages]


def _ker_pnsgk_coh_update_atom(F, K, A, X0, atom_index, atom_usages, params):
    # update error
    E = _nsgk_update_atom.E
    F = (E[:, atom_usages] +
         np.outer(A[:, atom_index], X0[atom_index, atom_usages].T))

    sel = [True] * A.shape[1]
    sel[atom_index] = False

    a = (K @ F @ X0[atom_index, atom_usages].T - 2 * params['gamma'] *
         K @ A[:, sel] @ A[:, sel].T @ K @ A[:, atom_index])
    a_norm = np.linalg.norm(a)
    if a_norm >= params['atom_norm_tolerance']:
        a /= np.sqrt(a.T @ K @ a)

    return a, X0[atom_index, atom_usages]


def nsgk(Y, D, X, params):
    '''
    New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # init current representation matrix
    if not hasattr(_nsgk_update_atom, 'X0'):
        _nsgk_update_atom.X0 = X

    # update current error
    _nsgk_update_atom.E = Y - D @ X

    D, _ = _update_atom(Y, D, _nsgk_update_atom.X0, params, _nsgk_update_atom)

    # update current representation matrix
    _nsgk_update_atom.X0 = X

    return D, X


def nsgk_reg(Y, D, X, params):
    '''
    Regularized New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    # init current representation matrix
    if not hasattr(_nsgk_update_atom, 'X0'):
        _nsgk_update_atom.X0 = X

    # update current error
    _nsgk_update_atom.E = Y - D @ X

    D, _ = _update_atom(Y, D, _nsgk_update_atom.X0, params, _nsgk_update_atom)

    # update current representation matrix
    _nsgk_update_atom.X0 = X

    return D, X


def nsgk_coh(Y, D, X, params):
    '''
    New Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    # init current representation matrix
    if not hasattr(_nsgk_coh_update_atom, 'X0'):
        _nsgk_coh_update_atom.X0 = X

    # update current error
    _nsgk_coh_update_atom.E = Y - D @ X

    D, _ = _update_atom(Y, D, _nsgk_coh_update_atom.X0,
                        params, _nsgk_coh_update_atom)

    # update current representation matrix
    _nsgk_coh_update_atom.X0 = X

    return D, X


def pnsgk(Y, D, X, params):
    '''
    Parallel New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # init current representation matrix
    if not hasattr(_pnsgk_update_atom, 'X0'):
        _pnsgk_update_atom.X0 = X

    # update current error
    _pnsgk_update_atom.E = Y - D @ X

    D, _ = _update_patom(Y, D, _pnsgk_update_atom.X0,
                         params, _pnsgk_update_atom)

    # update current representation matrix
    _pnsgk_update_atom.X0 = X

    return D, X


def pnsgk_reg(Y, D, X, params):
    '''
    Parallel Regularized New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    # init current representation matrix
    if not hasattr(_pnsgk_update_atom, 'X0'):
        _pnsgk_update_atom.X0 = X

    # update current error
    _pnsgk_update_atom.E = Y - D @ X

    D, _ = _update_patom(Y, D, _pnsgk_update_atom.X0,
                         params, _pnsgk_update_atom)

    # update current representation matrix
    _pnsgk_update_atom.X0 = X

    return D, X


def pnsgk_coh(Y, D, X, params):
    '''
    Parallel New Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    # init current representation matrix
    if not hasattr(_pnsgk_coh_update_atom, 'X0'):
        _pnsgk_coh_update_atom.X0 = X

    # update current error
    _pnsgk_coh_update_atom.E = Y - D @ X

    D, _ = _update_patom(Y, D, _pnsgk_coh_update_atom.X0,
                         params, _pnsgk_coh_update_atom)

    # update current representation matrix
    _pnsgk_coh_update_atom.X0 = X

    return D, X


def ker_nsgk(K, A, X, params):
    '''
    Kernel New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_nsgk_update_atom)
    return A, X


def ker_nsgk_reg(K, A, X, params):
    '''
    Regularized New Kernel New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params.regmu)

    A, X = _update_atom_ker(K, A, X, params, _ker_nsgk_update_atom)
    return A, X


def ker_nsgk_coh(K, A, X, params):
    '''
    Kernel New Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_nsgk_coh_update_atom)
    return A, X


def ker_pnsgk(K, A, X, params):
    '''
    Parallel Kernel New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_nsgk_update_atom)
    return A, X


def ker_pnsgk_reg(K, A, X, params):
    '''
    Parallel Regularized Kernel New Sequential Generalization of the K-means algorithm.
    The parameters are the same as for K-SVD.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = ker_omp_postreg(K, A, X, params['regmu'])

    A, X = _update_patom_ker(K, A, X, params, _ker_nsgk_update_atom)
    return A, X


def ker_pnsgk_coh(K, A, X, params):
    '''
    Parallel Kernel New Sequential Generalization of the K-means algorithm with coherence reduction.
    The parameters are the same as for K-SVD.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_nsgk_coh_update_atom)
    return A, X
