from crikit.fe import *
from crikit.fe_adjoint import *
from pyadjoint.tape import annotate_tape, get_working_tape, stop_annotating
from pyadjoint.overloaded_type import create_overloaded_object
import jax
from jax import numpy as jnp
from jax import random
import numpy as np
from pyadjoint_utils import Block
from pyadjoint_utils.jax_adjoint import array, ndarray, overload_jax
from pyadjoint.tape import annotate_tape, stop_annotating, get_working_tape
from crikit.cr.jax_utils import (
    JAXArrays,
    UFLExprSpace_To_JAX,
    JAX_UFLFunctionSpace_Covering,
)
from crikit.cr.ufl import UFLExprSpace
from crikit.cr.types import PointMap
from crikit.covering import get_composite_cr
from typing import Optional, List


def u_observer(u):
    return u.copy(deepcopy=True)


class SurfaceObserver:
    class SurfaceObservation:
        def __init__(self, u, de):
            self.u = u.copy(deepcopy=True)
            self.de = de

    def __init__(self, de):
        self.de = de

    def __call__(self, u):
        return self.SurfaceObservation(u, self.de)


class SubdomainObserver:
    def __init__(self, mesh: Mesh, subdomain: SubDomain):
        """An Observer that zeros all values of a :class:`Function` outside of a certain :class:`SubDomain`.

        :param mesh: The mesh
        :type mesh: (~fenics.Mesh)
        :param subdomain: The subdomain
        :type subdomain: SubDomain
        :return: The SubdomainObserver
        :rtype: SubdomainObserver
        """
        self._cell_func = MeshFunction("size_t", mesh, mesh.topology().dim(), 0)
        self._subdomain = subdomain
        self._subdomain.mark(self._cell_func, 1)

    def __call__(self, u: Function) -> Function:
        """Compute the observation by zeroing out values off of the SubDomain.

        :param u: The :class:`Function` to observe
        :type u: Function
        :return: The observed `u`
        :rtype: Function
        """
        annotate = annotate_tape()
        with stop_annotating():
            obs = self._zero_complement(u.copy(deepcopy=True), 1)
        if annotate_tape:
            obs = create_overloaded_object(obs)
            block = SubdomainObserverBlock(create_overloaded_object(u), obs, self)
            tape = get_working_tape()
            tape.add_block(block)

        return obs

    def _zero_complement(self, u, subdomain_id):
        u_vec_cpy = self._zero_complement_vec(u, u.vector(), subdomain_id)
        u.vector().set_local(u_vec_cpy.get_local())
        return u

    def _zero_complement_vec(self, u_func, u_vec, subdomain_id):
        # create a Function like u that's 1 everywhere on the subdomain, 0 off of it
        # and use that to determine which indices of u to zero out
        ucb = (
            Constant((1,) * u_func.ufl_shape[0])
            if len(u_func.ufl_shape) > 0
            else Constant(1)
        )
        dbc = DirichletBC(u_func.function_space(), ucb, self._subdomain)
        v = Function(u_func.function_space())
        dbc.apply(v.vector())
        idx = np.where(v.vector().vec().array != 1)
        uc = u_vec.copy()
        u_locals = uc.get_local()
        u_locals[idx] = 0.0
        uc.set_local(u_locals)
        return uc


class SubdomainObserverBlock(Block):
    def __init__(self, var, output, observer):
        super().__init__()
        self.observer = observer
        self.add_dependency(var)
        self.add_output(output.create_block_variable())

    def recompute_component(self, inputs, block_variable, idx, prepared):
        return self.observer._zero_complement(inputs[0].copy(deepcopy=True), 1)

    def evaluate_adj_component(self, inputs, adj_inputs, block_variable, idx, prepared):
        return self.observer._zero_complement_vec(inputs[0], adj_inputs[0], 1)

    def evaluate_tlm_component(self, inputs, tlm_inputs, block_variable, idx, prepared):
        return self.observer._zero_complement(tlm_inputs[0], 1)

    def evaluate_hessian_component(
        self, inputs, hessian_inputs, adj_inputs, block_variable, prepared
    ):
        return self.evaluate_adj_component(
            inputs, hessian_inputs, block_variable, idx, prepared
        )


class AdditiveRandomFunction:
    """A class representing a random function on a mesh that adds a sample
    from its distribution to the inputs (i.e. an additive noise model). In
    other words, if ``X`` is your UFL input and ``Y`` is the random variable
    this class represents, then this class returns ``X + Y``.
    """

    def __init__(
        self,
        V: FunctionSpace,
        distribution: Optional[str] = "normal",
        seed: Optional[int] = 0,
        **kwargs,
    ):
        """
        :param V: The ``FunctionSpace`` in which to generate noise
        :type V: FunctionSpace
        :param distribution: A string describing the distribution of this function. Use the static method :meth:`AdditiveRandomFunction.available_distributions` to see available distributions, defaults to 'normal'
        :type distribution: str, optional
        :param seed: the seed for ``jax.random``, defaults to 0
        :type seed: int, optional
        :param kwargs: Keyword arguments (e.g. parameter values) to be passed
            on to the distribution. For example, if ``distribution`` is 'gamma',
            you should pass ``a = value_of_a``, since ``jax.random.gamma`` takes
            a parameter named ``a``.
        :type kwargs: dict, optional

        """
        self._V = V
        self._key = random.PRNGKey(seed)
        self._kwargs = kwargs
        dmap = self._get_distribution_map()
        if distribution not in dmap:
            raise ValueError(
                f"Distribution {distribution} is not in the list of available distributions! The list of available distributions is \n{list(dmap.keys())}."
            )

        self._distribution = dmap[distribution.lower()]
        self._dname = distribution.lower()

    def __str__(self):
        return (
            f"AdditiveRandomFunction(distribution={self._dname}, kwargs={self._kwargs})"
        )

    def __call__(self, ufl_input: Function) -> Function:
        """Generate and add the noise.

        :param ufl_input: The input
        :type ufl_input: Function
        :return: The input plus some random noise
        :rtype: Function
        """
        annotate = annotate_tape()
        with stop_annotating():
            noise_f = Function(self._V)
            self._kwargs["shape"] = noise_f.vector().vec().array.shape
            self._key, subkey = random.split(self._key)
            noise = self._distribution(subkey, **self._kwargs)
            noisy_ufl = ufl_input.copy(deepcopy=True)
            noisy_ufl.vector()[:] += noise

        if annotate:
            tape = get_working_tape()
            tape.add_block(AdditiveRandomBlock(ufl_input, noisy_ufl, noise))

        return noisy_ufl

    @staticmethod
    def _normal(key, **kwargs):
        std = kwargs.pop("std", 1.0)
        mu = kwargs.pop("mu", 0.0)
        return std * random.normal(key, **kwargs) + mu

    @staticmethod
    def _get_distribution_list() -> List[str]:
        """Returns a list of available distributions
        :return: list of strings that can be passed to the constructor as distributions
        :rtype: list
        """
        return list(AdditiveRandomFunction._get_distribution_map().keys())

    @staticmethod
    def get_available_params() -> dict:
        """
        Returns a dictionary mapping distribution names to the names of
        parameters for that distribution (pass as kwargs to the constructor for
        this class). For example, if you're using a ``pareto`` distribution,
        you'll also want to pass ``b=your_b_value`` to the constructor of this class.

        Currently, that dictionary is
        ::

            {'bernoulli' : 'p',
                'beta' : 'a, b',
                'dirichlet' : 'alpha',
                'double_sided_maxwell' : 'loc, scale',
                'gamma' : 'a',
                'multivariate_normal' : 'mean, cov',
                'normal' : 'mu, std',
                'pareto' : 'b',
                'poisson' : 'lam',
                't' : 'df',
                'truncated_normal' : 'lower, upper',
                'uniform' : 'minval, maxval',
                'weibull' : 'concentration'
             }

        """
        return {
            "bernoulli": "p",
            "beta": "a, b",
            "dirichlet": "alpha",
            "double_sided_maxwell": "loc, scale",
            "gamma": "a",
            "multivariate_normal": "mean, cov",
            "normal": "mu, std",
            "pareto": "b",
            "poisson": "lam",
            "t": "df",
            "truncated_normal": "lower, upper",
            "uniform": "minval, maxval",
            "weibull": "concentration",
        }

    @staticmethod
    def _get_distribution_map():
        return {
            "bernoulli": random.bernoulli,
            "cauchy": random.cauchy,
            "dirichlet": random.dirichlet,
            "double_sided_maxwell": random.double_sided_maxwell,
            "exponential": random.exponential,
            "gamma": random.gamma,
            "gumbel": random.gumbel,
            "laplace": random.laplace,
            "logistic": random.logistic,
            "maxwell": random.maxwell,
            "multivariate_normal": random.multivariate_normal,
            "normal": AdditiveRandomFunction._normal,
            "pareto": random.pareto,
            "poisson": random.poisson,
            "rademacher": random.rademacher,
            "t": random.t,
            "truncated_normal": random.truncated_normal,
            "uniform": random.uniform,
            "weibull": random.weibull_min,
        }

    @staticmethod
    def available_distributions() -> List[str]:
        return AdditiveRandomFunction._get_distribution_list()


class AdditiveRandomBlock(Block):
    def __init__(self, var, output, noise):
        super().__init__()
        self.noise = noise
        self.add_dependency(var)
        self.add_output(output.create_block_variable())

    def recompute_component(self, inputs, block_variable, idx, prepared):
        var = inputs[0].copy(deepcopy=True)
        var.vector()[:] += self.noise
        return var

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return adj_inputs[0]

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return tlm_inputs[0]

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return inputs[0]

    def evaluate_hessian_component(
        self,
        inputs,
        hessian_inputs,
        adj_inputs,
        block_variable,
        idx,
        relevant_dependencies,
        prepared=None,
    ):
        return hessian_inputs[0]
