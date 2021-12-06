import scipy
import numpy as np


def _cholupdate(L, x):
    n = len(x)

    for k in range(n):
        r = np.sqrt(L[k, k]**2 + x[k]**2)
        c = r / L[k, k]
        s = x[k] / L[k, k]
        L[k, k] = r

        if k < n:
            L[k+1:n, k] = (L[k+1:n, k] + s * x[k+1:n]) / c
            x[k+1:n] = c * x[k+1:n] - s * L[k+1:n, k]

    return L


def ocddl(y, D, x, params):
    """
    Online Coordinate Descent Dictionary Learning
    """
    ocddl.A = params['ff'] * ocddl.A + x @ x.T
    ocddl.B = params['ff'] * ocddl.B + np.outer(y, x.T)

    for atom_index in range(D.shape[1]):
        D[:, atom_index] = (D[:, atom_index] + (ocddl.B[:, atom_index] -
                            D @ ocddl.A[:, atom_index]) /
                            ocddl.A[atom_index, atom_index])

        d_norm = np.linalg.norm(D[:, atom_index])
        if d_norm >= params['atom_norm_tolerance']:
            D[:, atom_index] /= d_norm

    return D, x


def rlsdl(y, D, x, params):
    """
    Recursive Least Squares Dictionary Learning
    """

    # Compute error
    r = y - D @ x

    # Compute auxiliary variables
    u = scipy.linalg.solve_triangular(rlsdl.A, x, lower=False, trans=1)
    u = scipy.linalg.solve_triangular(rlsdl.A, u, lower=False) / params['ff']
    alpha = 1 / (1 + x.T @ u)

    # Update inverse
    rlsdl.A = _cholupdate(rlsdl.A, x).T

    # Compute dictionary
    D = D + alpha * np.outer(r, u)

    # Normalize dictionary columns
    D = D / np.linalg.norm(D, axis=0)

    return D, x
