import numpy as np

from sklearn.linear_model import OrthogonalMatchingPursuit


def omp(Y, D, n_nonzero_coefs):
    """Orthogonal Matching Pursuit wrapper

    Parameters
    ----------
    Y : ndarray of shape (n_samples, n_features)
        Data matrix.

    D : ndarray of shape (n_components, n_features)
        Initial dictionary, with normalized columns.

    n_nonzero_coefs : int, default=None
        Desired number of non-zero entries in the solution. If None (by default)
        this value is set to 10% of n_features.


    Returns
    -------
    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    err : float
          The approximation error


    Example::

        X, err = omp(Y, D, n_nonzero_coefs)
    """
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=n_nonzero_coefs)
    X = omp.fit(D, Y).coef_.T
    err = (np.linalg.norm(Y - D @ X, 'fro') /
           np.sqrt(Y.size))
    return X, err


def omp_2d(Y, D, n_nonzero_coefs):
    """Orthogonal Matching Pursuit 2D wrapper

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        The dictionary matrix against which to solve the sparse coding of
        the data. Some of the algorithms assume normalized cols.

    n_nonzero_coefs : int, default=None
        Desired number of non-zero entries in the solution. If None (by default)
        this value is set to 10% of n_features.


    Returns
    -------
    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    err : float
          The approximation error


    Example::

        X, err = omp_2d(Y, D, n_nonzero_coefs)
    """
    ompfun = OrthogonalMatchingPursuit(n_nonzero_coefs=n_nonzero_coefs)
    Y_vec = Y.reshape(Y.shape[0], Y.shape[1]*Y.shape[2]).T
    D_vec = np.kron(D[0], D[1])

    codes_vec = ompfun.fit(D_vec, Y_vec).coef_.T

    err = np.linalg.norm(Y_vec - D_vec@codes_vec, 'fro') / np.sqrt(Y.size)
    X = codes_vec.T.reshape(Y.shape[0],
                            D[0].shape[0],
                            D[1].shape[0])
    return X, err


def omp_postreg(Y, D, X, mu):
    """Post Orthogonal Matching Pursuit regularization.
    Solve regularized least squares problem on support computed by OMP or other sparse encoder.

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        The dictionary matrix against which to solve the sparse coding of
        the data. Some of the algorithms assume normalized cols.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.
        
    mu : float
         The regularization factor


    Returns
    -------
    X : ndarray of shape (n_components, n_samples)
        The sparse codes.


    Example::

        X = omp_postreg(Y, D, X, mu)
    """
    for j in range(Y.shape[1]):
        atom_usages = np.nonzero(X[:, j])[0]
        d = D[:, atom_usages]
        X[atom_usages, j] = np.linalg.solve(
            d.T @ d + mu*np.eye(d.shape[1]),
            d.T @ Y[:, [j]]
        ).reshape(-1)
    return X


def ker_omp_postreg(K, A, X, mu):
    """Post Kernel Orthogonal Matching Pursuit regularization.
    Solve regularized least squares problem on support computed by OMP or other sparse encoder.

    Parameters
    ----------
    K : ndarray of shape (n_samples, n_samples)
        Kernel matrix.

    A : ndarray of shape (n_samples, n_components)
        The dictionary matrix against which to solve the sparse coding of
        the data. Some of the algorithms assume normalized cols.

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.
        
    mu : float
         The regularization factor


    Returns
    -------
    X : ndarray of shape (n_components, n_samples)
        The sparse codes.


    Example::

        X = ker_omp_postreg(K, A, X, mu)
    """
    for j in range(K.shape[1]):
        data_indices = np.nonzero(X[:, j])[0]
        A_j = A[:, data_indices]
        X[data_indices, j] = np.linalg.solve(
            A_j.T @ K @ A_j + mu*np.eye(A_j.shape[1]),
            A_j.T @ K[:, j]
        ).reshape(-1)
    return X
