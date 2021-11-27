from jax import jit
import jax.numpy as np
import numpy as onp
from jax.tree_util import Partial as partial
from itertools import chain, combinations


@jit
def symm(x):
    """Symmetrizes the input

    :param x: a 2-d array to symmetrize
    :type x: Union[np.ndarray,onp.ndarray]
    :return: A symmetric (and doubled) version of ``x``
    :rtype: Union[np.ndarray,onp.ndarray]

    """
    return x + x.T


@jit
def antisymm(x):
    """Antisymmetrizes the input

    :param x: a 2-d array to antisymmetrize
    :type x: Union[np.ndarray,onp.ndarray]
    :return: An antisymmetric (and doubled) version of ``x``
    :rtype: Union[np.ndarray,onp.ndarray]

    """
    return x - x.T


@jit
def commutator_action(A, B, v):
    bv = B @ v
    av = A @ v
    return A @ bv - B @ av


@jit
def anticommutator_action(A, B, v):
    Av = A @ v
    Bv = B @ v
    return A @ Bv + B @ Av


@jit
def scalar_triple_prod(u, v, w):
    return np.dot(v, np.cross(u, w))


# Copied from https://docs.python.org/3/library/itertools.html
def powerset(iterable, exclude_empty_set=True):
    "powerset([1,2,3], False) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = tuple(iterable)
    return chain.from_iterable(
        combinations(s, r) for r in range(int(exclude_empty_set), len(s) + 1)
    )


def levi_civita(n):
    """Returns the Levi-Civita pseudotensor in ``n`` dimensions.

    :param n: the number of dimensions
    :type n: int
    :returns: The Levi-Civita pseudotensor in ``n`` spatial dimensions
    :rtype: np.ndarray

    """
    if n == 2:
        return np.array([[0, 1], [-1, 0]])
    elif n == 3:
        eps = onp.zeros((3, 3, 3))
        pos_idx = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
        neg_idx = [(2, 1, 0), (0, 2, 1), (1, 0, 2)]
        for ix, iy, iz in pos_idx:
            eps[ix, iy, iz] = 1

        for ix, iy, iz in neg_idx:
            eps[ix, iy, iz] = -1

        return np.array(eps)
    else:
        raise NotImplementedError


eps_ijk = levi_civita(3)
eps_ij = levi_civita(2)


@jit
def _eps_vec_action(v):
    return np.einsum("ijk,k -> ij", eps_ijk, v)


@jit
def axial_vector(G):
    return np.einsum("ijk,jk->i", eps_ijk, G, optimize=True)


@jit
def _tprod(x, y):
    return np.tensordot(x, y, axes=0)


def symm_q4(T):
    S = np.zeros_like(T)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    idx = (i, j, k, l)
                    for pi in permutations(idx):
                        S = jax.ops.index_add(S, idx, T[tuple(pi)])

    return S


@jit
def symm_q3(T):
    return (
        T + np.moveaxis(T, [0, 1, 2], [1, 2, 0]) + np.moveaxis(T, [0, 1, 2], [2, 0, 1])
    )


@jit
def tA(T, A):
    return np.einsum("ijk,jk -> i", T, A, optimize=True)


@jit
def tv(T, v):
    return tA(T, _tprod(v, v))


@jit
def Tv(T, v):
    return np.einsum("ijk,k -> ij", T, v, optimize=True)


@jit
def TinnerS(T, S):
    return np.einsum("ijk,jkl -> il", T, S, optimize=True)


@jit
def TcontrS(T, S):
    return np.einsum("ijk,ijk", T, S, optimize=True)


@jit
def TW(T, W):
    return np.einsum("ijm,mk -> ijk", T, W, optimize=True)


@jit
def tbrace(T):
    # eq 2.34 in Zheng '94
    return [
        T,
        np.moveaxis(T, [1, 2, 3], [2, 3, 1]),
        np.moveaxis(T, [1, 2, 3], [3, 1, 2]),
    ]


@jit
def near(y, x, tol):
    return np.abs(x - y) <= tol


@jit
def _is_third_order_irreducible(T):
    if len(T.shape) != 3:
        return False

    t1 = T[1, 1, 1]
    t2 = T[2, 2, 2]
    t1id = (1, 1, 1)
    t2id = (2, 2, 2)
    t1idx = {(1, 2, 2), (2, 1, 2), (2, 2, 1)}
    t2idx = {(2, 1, 1), (1, 2, 1), (1, 1, 2)}
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            for k in range(t.shape[2]):
                idx = (i, j, k)
                if idx == t1id or idx == t2id:
                    continue

                if idx in t1idx:
                    if not near(T[idx], -t1, 1.0e-10):
                        return False
                elif idx in t2idx:
                    if not near(T[idx], -t2, 1.0e-10):
                        return False
                else:
                    if not near(T[idx], 0.0, 1.0e-10):
                        return False

    return True


@partial(jit, static_argnums=(1,))
def spectral_decomp(A, hermitian=False):
    w, V = np.linalg.eigh(A) if hermitian else np.linalg.eig(A)
    return V, np.diag(w)


def factorial(n: int):
    if n == 0:
        return 1
    return np.prod(np.arange(1, n + 1))


# @partial(jit,static_argnums=(2,))
def matpows(A, ns, hermitian=False):
    # TODO: use a better algorithm for this, maybe exponentiation by squaring?
    V, D = spectral_decomp(A, hermitian)
    Vinv = np.linalg.inv(V)
    return [Vinv @ np.power(D, i) @ V for i in ns]


def matexp(A, hermitian=False):
    # TODO: find actually good choices of these parameters
    N = range(10)
    return sum([A_i / factorial(i) for A_i, i in zip(matpows(A, N, hermitian), N)])


@jit
def _3d_rotation_matrix(axis, theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    ux = axis[0]
    uy = axis[1]
    uz = axis[2]
    return np.array(
        [
            [
                ct + ux * ux * (1 - ct),
                ux * uy * (1 - ct) - uz * st,
                ux * uz * (1 - ct) + uy * st,
            ],
            [
                uy * ux * (1 - ct) + uz * st,
                ct + uy * uy * (1 - ct),
                uy * uz * (1 - ct) - ux * st,
            ],
            [
                uz * ux * (1 - ct) - uy * st,
                uz * uy * (1 - ct) + ux * st,
                ct + uz * uz * (1 - ct),
            ],
        ]
    )


@jit
def householder_matrix(v):
    return np.eye(v.size) - _tprod(v, v)


def near(val, to, rtol=1.0e-5):
    """Returns True if ``val`` and ``to`` are within relative tolerance ``rtol``
    and False otherwise

    :param val: a value
    :type val: np.ndarray
    :param to: is ``val`` close to this?
    :type to: np.ndarray
    :param rtol: Relative tolerance, defaults to 1.0e-5
    :type rtol: float, optional
    :return: are ``val`` and ``to`` within ``rtol``?
    :rtype: bool

    """
    # effectively a JAX DeviceArray( ,dtype=bool) to bool conversion
    return bool(np.allclose(val, to, rtol=rtol))


def is_symm(X, rtol=1.0e-5):
    return near(X, 0.5 * symm(X), rtol)


def is_antisymm(X, rtol=1.0e-5):
    return near(X, 0.5 * antisymm(X), rtol)
