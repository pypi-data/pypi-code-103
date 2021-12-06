import scipy
import numpy as np

from ._omp import omp_postreg, ker_omp_postreg
from ._atom import (_update_atom, _update_patom,
                    _update_atom_ker, _update_patom_ker)
 

def _ksvd_update_atom(F, D, X, atom_index, atom_usages, params):
    # TODO improve svds from scipy
    U, S, Vh = np.linalg.svd(F, full_matrices=False)
    d = U[:, 0]
    x = S[0] * Vh[0, :]
    return d, x


def _ksvd_reg_update_atom(F, D, X, atom_index, atom_usages, params):
    # TODO improve svds from scipy
    U, S, Vh = np.linalg.svd(F, full_matrices=False)
    d = U[:, 0]
    x = S[0] * Vh[0, :] / (1 + params['regmu'])
    return d, x


def _ksvd_coh_update_atom(F, D, X, atom_index, atom_usages, params):
    sel = [True] * D.shape[1]
    sel[atom_index] = False

    H = F @ F.T - 2 * params['gamma'] * D[:, sel] @ D[:, sel].T
    _, d = scipy.sparse.linalg.eigs(H, k=1)
    d = np.ravel(d)
    x = F.T @ d
    return d, x


def _ker_ksvd_update_atom(F, K, A, X, atom_index, atom_usages, params):
    # TODO improve svds from scipy
    s, v = scipy.sparse.linalg.eigs(F.T @ K @ F, k=1)
    s = np.sqrt(s)
    a = F @ v / s
    x = s * v
    return a, x


def _ker_ksvd_reg_update_atom(F, K, A, X, atom_index, atom_usages, params):
    # TODO improve svds from scipy
    s, v = scipy.sparse.linalg.eigs(F.T @ K @ F, k=1)
    s = np.sqrt(s)
    a = F @ v / s
    x = s * v / (1 + params['regmu'])
    return a, x


def _ker_ksvd_coh_update_atom(F, K, A, X, atom_index, atom_usages, params):
    sel = [True] * A.shape[1]
    sel[atom_index] = False

    H = K @ F @ F.T @ K - 2 * params['gamma'] * K @ A[:, sel] @ A[:, sel].T @ K
    _, a = scipy.sparse.linalg.eigs(H, k=1)
    a = np.ravel(a)
    x = F.T @ a
    return a, x


def ksvd(Y, D, X, params):
    '''K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The updated dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    D, X = _update_atom(Y, D, X, params, _ksvd_update_atom)
    return D, X


def ksvd_reg(Y, D, X, params):
    '''Regularized K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The updated dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_atom(Y, D, X, params, _ksvd_reg_update_atom)
    return D, X


def ksvd_coh(Y, D, X, params):
    '''K-SVD algorithm with coherence reduction

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The updated dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    D, X = _update_atom(Y, D, X, params, _ksvd_coh_update_atom)
    return D, X


def pksvd(Y, D, X, params):
    '''Parallel K-SVD algorithm

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    D, X = _update_patom(Y, D, X, params, _ksvd_update_atom)
    return D, X


def pksvd_reg(Y, D, X, params):
    '''Regularized Parallel K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    D, X = _update_patom(Y, D, X, params, _ksvd_reg_update_atom)
    return D, X


def pksvd_coh(Y, D, X, params):
    '''Parallel K-SVD with coherence reduction

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    D : ndarray of shape (n_features, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    D, X = _update_patom(Y, D, X, params, _ksvd_coh_update_atom)
    return D, X


def ker_ksvd(K, A, X, params):
    '''Kernel K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_ksvd_update_atom)
    return A, X


def ker_ksvd_reg(K, A, X, params):
    '''Regularized Kernel K-SVD
    
    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_ksvd_reg_update_atom)
    return A, X


def ker_ksvd_coh(K, A, X, params):
    '''Kernel K-SVD with coherence reduction

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    A, X = _update_atom_ker(K, A, X, params, _ker_ksvd_coh_update_atom)
    return A, X


def ker_pksvd(K, A, X, params):
    '''Parallel Kernel K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.   
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_ksvd_update_atom)
    return A, X


def ker_pksvd_reg(K, A, X, params):
    '''Parallel Regularized Kernel K-SVD

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_ksvd_reg_update_atom)
    return A, X


def ker_pksvd_coh(K, A, X, params):
    '''Parallel Kernel K-SVD with coherence reduction

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    A : ndarray of shape (n_samples, n_components)
        Initial dictionary, with normalized columns.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    params : dict
        Dictionary instance with provided parameters for the DL problem.
    
    Returns
    -------
    A : ndarray of shape (n_samples, n_components)
        The update dictionary matrix.

    X : ndarray of shape (n_components, n_samples)
        The updated sparse codes.
    '''
    A, X = _update_patom_ker(K, A, X, params, _ker_ksvd_coh_update_atom)
    return A, X
