import numpy as np

from ._omp import omp_postreg
from sklearn.preprocessing import normalize


def mod(Y, D, X, params):
    """
    Method of Optimal Directions.
    The parameters are the same as for K-SVD.
    """
    # Use SVD to avoid the singularity
    # issues when plainly solving the system
    U, S, Vh = np.linalg.svd(X, full_matrices=False)
    for i in range(len(S)):
        if S[i] < params['threshold_svd']:
            S[i] = 0
        else:
            S[i] = 1 / S[i]

    # compute dictionary
    D = np.linalg.multi_dot([Y, Vh.T, (U * S).T])

    # normalize dictionary columns
    # D = D / np.linalg.norm(D, axis=0)
    D = normalize(D, axis=0, norm='l2')

    return D, X


def mod_reg(Y, D, X, params):
    """
    Regularized Method of Optimal Directions.
    The parameters are the same as for K-SVD.
    """
    # Use sparse pattern from OMP to
    # compute new sparse representations
    X = omp_postreg(Y, D, X, params['regmu'])

    # Use SVD to avoid the singularity
    # issues when plainly solving the system
    U, S, Vh = np.linalg.svd(X, full_matrices=False)
    for i in range(len(S)):
        if S[i] < params['threshold_svd']:
            S[i] = 0
        else:
            S[i] = 1 / S[i]

    # compute dictionary
    D = np.linalg.multi_dot([Y, Vh.T, (U * S).T])

    # normalize dictionary columns
    # D = D / np.linalg.norm(D, axis=0)
    D = normalize(D, axis=0, norm='l2')

    return D, X


def ker_mod(K, A, X, params):
    """
    Kernel Method of Optimal Directions.
    The parameters are the same as for K-SVD.
    """
    # Use SVD to avoid the singularity
    # issues when plainly solving the system
    U, S, Vh = np.linalg.svd(X, full_matrices=False)
    for i in range(len(S)):
        if S[i] < params['threshold_svd']:
            S[i] = 0
        else:
            S[i] = 1 / S[i]

    # compute dictionary
    A = np.linalg.multi_dot([Vh.T, (U * S).T])

    # normalize dictionary columns
    # A = A / np.sqrt(np.diag(A.T @ K @ A))

    return A, X
