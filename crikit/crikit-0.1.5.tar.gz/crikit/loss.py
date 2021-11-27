from crikit.fe import *
from crikit.fe_adjoint import *
from crikit.observer import SurfaceObserver
from crikit.observe_block import observe_error
from pyadjoint_utils import Block, function_get_local
from pyadjoint_utils.jax_adjoint import array, ndarray, overload_jax
from pyadjoint.tape import annotate_tape, stop_annotating, get_working_tape
from crikit.cr.jax_utils import (
    JAXArrays,
    UFLExprSpace_To_JAX,
    JAX_UFLFunctionSpace_Covering,
)
from crikit.cr.ufl import UFLFunctionSpace
from crikit.cr.types import PointMap
from crikit.cr.space_builders import DirectSum
from crikit.covering import get_composite_cr
import jax
from jax import numpy as jnp
from jax.tree_util import Partial as partial
from jax import random
import numpy as np
from typing import Union, Optional


def integral_loss(
    meas: Union[Function, SurfaceObserver.SurfaceObservation], pred: Function
) -> AdjFloat:
    """Computes the squared L^2 loss between ``meas`` and ``pred``.

    :param meas: The observed data
    :type meas: Union[Function, SurfaceObserver.SurfaceObservation]
    :param pred: The observed data
    :type pred: Function
    :return: The integral of the squared difference between ``meas`` and ``pred``
    :rtype: AdjFloat
    """
    if isinstance(meas, SurfaceObserver.SurfaceObservation):
        # Integrate with the specified infinitesimal element.
        diff = pred.u - meas.u
        return assemble(inner(diff, diff) * meas.de)
    elif isinstance(meas, Function):
        # Integrate over the entire domain.
        diff = pred - meas
        return assemble(inner(diff, diff) * dx)


def vector_loss(meas, pred):
    return observe_error(pred, meas.vector())


class SlicedWassersteinDistance(PointMap):
    """A class that computes the sliced p-th Wasserstein distance, which is
    obtained by projecting the data into ``num_projections`` random directions,
    then computing the 1-dimensional p-th Wasserstein distances of the sliced
    data and averaging those.
    """

    def __init__(
        self,
        V: FunctionSpace,
        num_projections: int,
        key: int,
        p: int = 2,
        u_weights: Optional[jnp.ndarray] = None,
        v_weights: Optional[jnp.ndarray] = None,
    ):
        """

        :param V: The :class:`crikit.fe_adjoint.FunctionSpace` in which the
        inputs to this class live.
        :type V: crikit.fe_adjoint.FunctionSpace
        :param num_projections: How many random directions to project the data in?
        :type num_projections: int
        :param key: the key for :mod:`jax.random` to use for sampling (i.e. result of a call to `jax.random.PRNGKey(seed)`)
        :type key: int
        :param p: the "p" in "p-th Wasserstein distance", defaults to 2
        :type p: int, optional
        :param u_weights: Optional weights to use for the first distribution passed to this class, defaults to None
        :type u_weights: jax.numpy.ndarray, optional
        :param v_weights: Optional weights to use for the second distribution passed to this class, defaults to None
        :type v_weights: jax.numpy.ndarray, optional
        """

        ufl_u = Function(V)
        qp_shape = ufl_u.ufl_shape
        n_qp = ufl_u.vector().vec().array.size // np.prod(qp_shape)
        jax_u = jnp.ones((n_qp, *qp_shape))
        self._backend = BackendSlicedWassersteinDistance(
            jax_u,
            jax_u,
            num_projections,
            key,
            u_weights=u_weights,
            v_weights=v_weights,
            p=p,
        )

        self._backend = get_composite_cr(
            DirectSum(UFLFunctionSpace(V), UFLFunctionSpace(V)), self._backend
        )

        super().__init__(self._backend.source, self._backend.target)

    def __call__(self, u: Function, v: Function) -> ndarray:
        """Computes the p-th sliced Wasserstein distance between ``u`` and ``v``.
        :param u: The values of the first distribution
        :type u: crikit.fe_adjoint.Function
        :param v: The values of the second distribution
        :type v: crikit.fe_adjoint.Function
        :return: The p-th sliced Wasserstein distance between ``u`` and ``v``
        :rtype: pyadjoint_utils.jax_adjoint.ndarray
        """
        return self._backend((u, v))


class BackendSlicedWassersteinDistance(PointMap):
    """This class computes the sliced Wasserstein distance with JAX
    inputs and outputs. It's intended to be put inside a driver that calls
    get_composite_cr() on it so it can take UFL inputs.
    """

    def __init__(self, u, v, num_projections, key, u_weights=None, v_weights=None, p=2):
        self._u = u
        self._v = v
        self._key = key
        self._n = int(num_projections)
        self._samples = [jnp.eye(1)] if u.shape[1] == 1 else []
        if u.shape[1] > 1:
            for i in range(self._n):
                self._key, subkey = random.split(self._key)
                d = random.normal(subkey, shape=(u.shape[1],))
                self._samples.append(d / jnp.linalg.norm(d))

        self._u_w = u_weights
        self._v_w = v_weights
        self._args = ()
        if self._u_w is not None:
            if self._v_w is None:
                self._v_w = jnp.ones_like(v)
            self._distance = (
                weighted_sliced_wasserstein_distance
                if p == 1
                else lambda u, v, d, uw, vw: weighted_sliced_wasserstein_p_distance(
                    u, v, d, uw, vw, p
                )
            )
            self._args = (self._u_w, self._v_w)
        elif self._v_w is not None:
            self._u_w = jnp.ones_like(u)
            self._distance = (
                weighted_sliced_wasserstein_distance
                if p == 1
                else lambda u, v, d, uw, vw: weighted_sliced_wasserstein_p_distance(
                    u, v, d, uw, vw, p
                )
            )
            self._args = (self._u_w, self._v_w)
        else:
            self._distance = (
                sliced_wasserstein_distance
                if p == 1
                else lambda u, v, d: sliced_wasserstein_p_distance(u, v, d, p)
            )

        in_types = DirectSum(JAXArrays(u.shape), JAXArrays(v.shape))
        out_type = JAXArrays((jnp.mean(jnp.array([0, 1]))).shape)
        super().__init__(in_types, out_type)

    @property
    def num_projections(self):
        return self._n

    @num_projections.setter
    def num_projections(self, n):
        self._n = n

    @property
    def u_weights(self):
        return self._u_w

    @u_weights.setter
    def u_weights(self, new_weights):
        self._u_w = new_weights
        if self._v_w is None:
            self._v_w = jnp.ones_like(self._v)
            self._distance = weighted_sliced_wasserstein_distance
            self._args = (self._u_w, self._v_w)

    @property
    def v_weights(self):
        return self._v_w

    @u_weights.setter
    def v_weights(self, new_weights):
        self._v_w = new_weights
        if self._u_w is None:
            self._u_w = jnp.ones_like(self._u)
            self._distance = weighted_sliced_wasserstein_distance
            self._args = (self._u_w, self._v_w)

    def __call__(self, val):
        u, v = val
        return self._distance(u, v, jnp.array(self._samples), *self._args)


@partial(overload_jax, argnums=(0, 1))
def sliced_wasserstein_distance(u, v, directions, *args):
    def body_fun(val, d):
        (u, v) = val
        uproj = u @ d
        vproj = v @ d
        return (u, v), wasserstein_distance_1d(uproj, vproj)

    (u, v), distances = jax.lax.scan(body_fun, (u, v), directions)
    return jnp.mean(distances)


@partial(overload_jax, argnums=(0, 1))
def weighted_sliced_wasserstein_p_distance(
    u, v, directions, uweights, vweights, p, *args
):
    def body_fun(val, d):
        (u, v, uw, vw) = val
        uproj = u @ d
        vproj = v @ d

        return (u, v, uw, vw), _weighted_cdf_distance(p, uproj, vproj, uw, vw)

    (u, v), distances = jax.lax.scan(body_fun, (u, v, uw, vw), directions)
    return jnp.mean(distances)


@partial(overload_jax, argnums=(0, 1))
def sliced_wasserstein_p_distance(u, v, directions, p, *args):
    def body_fun(val, d):
        (u, v, p) = val
        uproj = u @ d
        vproj = v @ d
        return (u, v, p), _cdf_distance(uproj, vproj, p)

    (u, v, p), distances = jax.lax.scan(body_fun, (u, v, p), directions)
    return jnp.mean(distances)


@partial(overload_jax, argnums=(0, 1))
def weighted_sliced_wasserstein_distance(u, v, directions, uweights, vweights, *args):
    def body_fun(val, d):
        (u, v, uw, vw) = val
        uproj = u @ d
        vproj = v @ d

        return (u, v, uw, vw), weighted_wasserstein_distance_1d(uproj, vproj, uw, vw)

    (u, v), distances = jax.lax.scan(body_fun, (u, v, uw, vw), directions)
    return jnp.mean(distances)


# implementation of the Wasserstein distance taken from scipy
def wasserstein_distance_1d(u, v):
    """1-D Wasserstein distance between two distributions
    :param u: The first distribution
    :type u: jnp.ndarray
    :param v: The second distribution
    :type v: jnp.ndarray
    :return: The Wasserstein distance between ``u`` and ``v``.
    :rtype: jnp.ndarray
    """
    u_sort = jnp.argsort(u)
    v_sort = jnp.argsort(v)

    values = jnp.sort(jnp.concatenate((u, v)))

    deltas = jnp.diff(values)
    u_idx = u[u_sort].searchsorted(values[:-1], "right")
    v_idx = v[v_sort].searchsorted(values[:-1], "right")

    u_cdf = u_idx / u.size
    v_cdf = v_idx / v.size
    return jnp.sum(jnp.multiply(jnp.abs(u_cdf - v_cdf), deltas))


def weighted_wasserstein_distance_1d(u, v, uweights, vweights):
    """1-D Wasserstein distance between two distributions
    :param u: The first distribution
    :param v: The second distribution
    :param uweights: The weights
    :return: The Wasserstein distance between ``u`` and ``v``.
    :rtype: jnp.ndarray
    """
    u_sort = jnp.argsort(u)
    v_sort = jnp.argsort(v)

    values = jnp.sort(jnp.concatenate((u, v)))

    deltas = jnp.diff(values)

    u_idx = u[u_sort].searchsorted(values[:-1], "right")
    v_idx = v[v_sort].searchsorted(values[:-1], "right")

    u_sort_cum = jnp.concatenate(([0], jnp.cumsum(uweights[u_idx])))
    v_sort_cum = jnp.concatenate(([0], jnp.cumsum(vweights[v_idx])))
    u_cdf = u_sort_cum[u_idx] / u_sort_cum[-1]
    v_cdf = v_sort_cum[v_idx] / v_sort_cum[-1]
    return jnp.sum(jnp.multiply(jnp.abs(u_cdf - v_cdf), deltas))


@jax.jit
def _cdf_distance(u, v, p):
    u_sort = jnp.argsort(u)
    v_sort = jnp.argsort(v)

    values = jnp.sort(jnp.concatenate((u, v)))

    deltas = jnp.diff(values)
    u_idx = u[u_sort].searchsorted(values[:-1], "right")
    v_idx = v[v_sort].searchsorted(values[:-1], "right")

    u_cdf = u_idx / u.size
    v_cdf = v_idx / v.size
    return jnp.power(
        jnp.sum(jnp.multiply(jnp.power(jnp.abs(u_cdf - v_cdf), p), deltas)), 1 / p
    )


@jax.jit
def _weighted_cdf_distance(p, u, v, uweights, vweights):
    u_sort = jnp.argsort(u)
    v_sort = jnp.argsort(v)

    values = jnp.sort(jnp.concatenate((u, v)))

    deltas = jnp.diff(values)

    u_idx = u[u_sort].searchsorted(values[:-1], "right")
    v_idx = v[v_sort].searchsorted(values[:-1], "right")

    u_sort_cum = jnp.concatenate(([0], jnp.cumsum(uweights[u_idx])))
    v_sort_cum = jnp.concatenate(([0], jnp.cumsum(vweights[v_idx])))
    u_cdf = u_sort_cum[u_idx] / u_sort_cum[-1]
    v_cdf = v_sort_cum[v_idx] / v_sort_cum[-1]

    return jnp.power(jnp.sum(jnp.multiply(jnp.power(jnp.abs(u - v), p), deltas)), 1 / p)
