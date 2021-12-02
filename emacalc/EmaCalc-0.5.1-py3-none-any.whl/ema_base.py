"""General utility classes and functions for internal use.

Defines class
PopulationMixtureBase --- container for common properties used by all model classes
    specifying the indexing of separate types of parameters, and
    mixture-model components, and
    a prior for all mixture-model components

NOTE: To make the model identifiable,
although both latent-variable locations and response thresholds are freely variable,
some prior restriction is necessary.

The present version simply fixes the latent-variable location at theta = 0,
given the FIRST scenario category,
in the index order defined by the EmaFrame instance.

Therefore, to make it easier to interpret results,
this first scenario category should be selected
as the most "natural" reference in the EMA study,
to which other scenarios may be related.
This simple approach is implemented in module function _theta_map(),
which may change in future versions.

*** Version history:
* Version 0.5.1
2021-11-26, allow ZERO Attributes, i.e., empty emf.attribute_grades
2021-12-01, cleanup some doc comments
2021-12-02, Attribute sensory location fixed == 0. for first Scenario category
            regardless of regression_effect specification.

* Version 0.5
2021-11-24, first published beta version
"""
# ****************** allow NO Attributes ********************
import numpy as np
from scipy.special import logit  # , logsumexp
import logging

from EmaCalc.gauss_gamma import GaussianRV

# ------------------------------------------------------
__version__ = "2021-11-26"

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST

PRIOR_PSEUDO_RESPONDENT = 0.2  # 0.1 -> higher inter-individual variance
# = prior total pseudo-count re ONE real respondent
# for fixed hyper-prior of all GMM components

PRIOR_PARAM_SCALE = 1.
# = main hyperprior scale of Gaussian model parameters,
# to be rescaled with the class scale of latent sensory variable

PRIOR_PREC_A = 0.01  # for most parameters
PRIOR_PREC_B = PRIOR_PARAM_SCALE


# ------------------------------------------------------------------
class PopulationMixtureBase:
    """Superclass for ema_model.EmaModel and its sub-models.
    All these objects share a common list of GaussianRV instances,
    which are components of population GMMs for model parameters.
    Sub-populations, represented by separate subject groups,
    share the same GMM components,
    and differ only in their mixture weights.

    Each sub-population GMM is prior for
    individual parameter distributions in the subject group.
    Each individual parameter distribution is represented by
    a large set of samples, stored as property IndividualModel.xi, with
    xi[s, :] = s-th sample of the parameter vector for ONE subject.

    All model classes share mapping properties
    for extracting parameter subsets
    from the array of parameter vectors.
    """
    def __init__(self, emf, effects, rv_class,
                 theta_map,
                 scenario_slices,
                 attribute_slices,
                 comp_prior, comp):
        """
        :param emf: single ema_data.EmaFrame instance,
        :param effects: iterable with regression-effect terms for attribute regression
            effects[i] = single key in emf.scenarios.keys() or tuple of such keys
        :param rv_class: latent sensory variable class,
            defining its distribution as either logistic or normal.
        :param theta_map: fixed 2D array to extract latent-variable location samples from xi array
        :param scenario_slices: list of slice objects, such that
            xi[:, scenario_slices[t]] = alpha = log-prob for scenarios in t-th test stage
        :param attribute_slices: list of slice objects, such that
            xi[:, attribute_slices[i]] = all (beta, eta) parameters for i-th Attribute
            where
            beta = xi[:, cls.attribute_slices[i]][:, :n_beta] = regression-effect parameters
            eta = xi[:, cls.attribute_slices[i]][:, n_beta:] = threshold parameters
            where
            n_beta = n of regression-effect parameters, same for each attribute question.
        :param comp_prior: single GaussianRV instance, prior for ALL GMM components,
        :param comp: list of GaussianRV instances,
            each representing ONE mixture component
            for parameter vector xi, in the total population,
        """
        self.emf = emf
        self.effects = effects
        self.rv_class = rv_class
        self.theta_map = theta_map
        self.scenario_slices = scenario_slices
        self.attribute_slices = attribute_slices
        self.comp_prior = comp_prior
        self.comp = comp

    @classmethod
    def initialize(cls, n_comp, emf, effects, rv_class):
        """Assign all parameter-extraction properties, and
        GaussianRV mixture components with correct size.
        :param n_comp: integer desired number of mixture components
        :param emf: single ema_data.EmaFrame instance,
            defining the experiment structure.
        :param effects: iterable with regression-effect terms for attribute regression
            effects[i] = single key in emf.scenarios.keys() or tuple of such keys
        :param rv_class: latent sensory variable class,
            defining its distribution as either logistic or normal.
        :return: None

        Result: all properties initialized
        """
        _check_effects(emf, effects)
        effects = [e_i if type(e_i) is tuple else (e_i,)
                   for e_i in effects]
        # = list of requested regression effects of scenario categories
        # to be estimated for their influence on ATTRIBUTE responses.
        # Each element MUST be a tuple with one or more scenario key(s).

        # Define mapping indices from rows of xi array to its parts:
        n_stages = emf.scenario_shape[0]
        n_scenarios = np.prod(emf.scenario_shape[1:], dtype=int)  # except stages
        scenario_slices = _make_slices(n_stages * [n_scenarios])
        # = list of slice objects, such that
        # xi[:, cls.scenario_slices[t]] = alpha = log-prob for scenarios in t-th test stage
        # i.e., n_stages slices with equal lengths, for all test stages.

        theta_map = _theta_map(emf, effects)
        # = fixed 2D array to extract latent-variable location samples from xi array

        n_beta = theta_map.shape[0]
        # = number of regression-effect parameters, same for every Attribute
        n_attr_param = [n_beta + len(ordinal_levels)
                        for ordinal_levels in emf.attribute_grades.values()]
        # n_attr_param[i] = total number of model params for i-th Attribute
        # NOTE: May be EMPTY if no Attributes are defined
        attribute_slices = _make_slices(n_attr_param,
                                        start=scenario_slices[-1].stop)
        # xi[:, cls.attribute_slices[i]] = all (beta, eta) parameters for i-th Attribute
        # where
        # beta = xi[:, cls.attribute_slices[i]][:, :n_beta] = regression-effect parameters
        # eta = xi[:, cls.attribute_slices[i]][:, n_beta:] = threshold parameters
        # where
        # n_beta = n of regression-effect parameters, same for each attribute question.
        if len(attribute_slices) > 0:
            n_parameters = attribute_slices[-1].stop
        else:
            n_parameters = scenario_slices[-1].stop

        # define mixture components:
        comp_prior = cls._make_prior(n_parameters, n_beta,
                                     attribute_slices, rv_class)
        # = single GaussianRV instance, prior for ALL GMM components,
        # fixed throughout the VI learning procedure.
        comp = [cls._make_prior(n_parameters, n_beta,
                                attribute_slices, rv_class)
                for _ in range(n_comp)]
        # = list of GaussianRV instances,
        # each representing ONE mixture component
        # for parameter vector xi, in the total population,
        # to be learned from observed data.
        # All comp are initialized equal, so far,
        # to be separated later, before VI learning.
        return cls(emf, effects, rv_class,
                   theta_map,
                   scenario_slices,
                   attribute_slices,
                   comp_prior, comp)

    @property
    def n_parameters(self):
        if len(self.attribute_slices) > 0:
            return self.attribute_slices[-1].stop
        else:
            return self.scenario_slices[-1].stop

    @property
    def n_beta(self):
        """Total number of regression-effect parameters, same for each Attribute
        """
        return self.theta_map.shape[0]

    @property
    def attribute_slice_dict(self):
        """
        :return: dict with elements (attribute_key, attribute_slice)
        """
        return dict((a, a_slice)
                    for (a, a_slice) in zip(self.emf.attribute_grades.keys(),
                                            self.attribute_slices))

    @staticmethod
    def _make_prior(n_parameters, n_beta,
                    attribute_slices, rv_class):  # ****** module function ? **********
        """Create hyperprior for parameter distribution in the total population
        :param n_parameters: total number of parameters
        :param n_beta: number of regression-effect parameters for each attribute
        :return: single GaussianRV instance
        """
        scale = PRIOR_PARAM_SCALE * np.ones(n_parameters)
        for a_slice in attribute_slices:
            scale[a_slice][:n_beta] *= rv_class.scale
        return GaussianRV(loc=np.zeros(n_parameters),
                          scale=scale,
                          learned_weight=PRIOR_PSEUDO_RESPONDENT)

    def scenario_prob(self, xi):
        """Extract probability-mass for scenarios, given parameters,
        used mainly by ema_display
        :param xi: 2D array with parameter samples
        :return: u = mD array with scenario probability-mass within each Stage,
            u[s, k0, k1, k2, ...] = s-th sample of P[(k1, k2,...)-th scenario | stage k0]
            sum u[s, k0] == 1., for all s and k0
        """
        n_sc = self.scenario_slices[-1].stop
        alpha = xi[:, :n_sc].reshape((xi.shape[0], self.emf.n_stages, -1))
        alpha -= np.amax(alpha, axis=-1, keepdims=True)
        u = np.exp(alpha)
        u /= np.sum(u, axis=-1, keepdims=True)
        return u.reshape((-1, *self.emf.scenario_shape))

    def attribute_theta(self, xi, a):
        """Extract location of latent sensory variable, for given attribute
        :param xi: 2D array with parameter sample vectors
            xi[s, :] = s-th parameter sample vector
        :param a: attribute key = one of self.emf.attribute_grades.keys()
        :return: theta = mD array, with
            theta[s, k0, k1, ...] = s-th sample of
                attribute location, given the (k0, k1, ...)-th scenario.
        """
        a_slice = self.attribute_slice_dict[a]
        beta = xi[..., a_slice][..., :self.n_beta]
        return np.dot(beta, self.theta_map).reshape((-1, *self.emf.scenario_shape))

    def attribute_tau(self, xi, a):
        """Extract response thresholds for given attribute
        :param xi: 2D array with parameter sample vectors
            xi[s, :] = s-th parameter sample vector
        :param a: attribute key = one of self.emf.attribute_grades.keys()
        :return: tau = mD array, with
            tau[s, l] = s-th sample of UPPER limit of l-th response interval,
                EXCEPT the last at +inf
                tau.shape[-1] == len(self.emf.attribute_grades[a]) - 1
        """
        a_slice = self.attribute_slice_dict[a]
        eta = xi[..., a_slice][..., self.n_beta:]
        return response_thresholds(eta)[..., 1:-1]


# ---------------------------------------- Module help functions:

def response_thresholds(log_w):
    """Transform given log-category-width parameters to response thresholds.
    :param log_w: 1D or 2D array with
        log_w[..., m] = ...-th sample of log non-normalized width of m-th interval.
        log_w.shape[-1] == M == number of response-scale intervals.
    :return: 1D or 2D array tau, with all elements in [-inf, +inf]
        (tau[..., m], tau[..., m+1] = (LOWER, UPPER) limits for m-th ordinal response interval
        tau[..., 0] ==  - np.inf
        tau[..., -1] == + np.inf
        tau.ndim == log_w.ndim; tau.shape[-1] == log_w.shape[-1] + 1

    Method:
        Normalized widths and interval limits are defined in transformed domain [0, 1.],
        using a logistic mapping function,
        y = expit(tau), where y in [0, 1],
            y[..., 0] = 0.
            y[..., m+1] =  (w_0 +...+ w_m) / (w_0 + ... + w_{M-1};  0 <= m <= M-1
            w_m = exp(log_w[..., m])
        Thus, cat_limits are calculated with the inverse transform
        tau = logit(y)
    """
    # w = np.exp(log_w)
    # = non-normalized width of transformed intervals, always > 0
    cum_w = np.cumsum(np.exp(log_w), axis=-1)
    z_shape = list(cum_w.shape)
    z_shape[-1] = 1
    cum_w = np.concatenate((np.zeros(z_shape), cum_w),
                           axis=-1)  # ****** use np.pad ???
    # sum_w = cum_w[..., -1:]
    return logit(cum_w / cum_w[..., -1:])


def d_response_thresholds(log_w):
    """Jacobian of cat_limits with respect to log_w
    :param log_w: 1D or 2D array (called eta in Leijon doc), with
        log_w[..., m] = ...-th sample of log non-normalized width of m-th interval,
        log_w.shape[-1] = M = number of response intervals
    :return: 2D or 3D array d_tau, with
        d_tau[..., m, i] = d tau[..., m] / d log_w[..., i]; m = 0,..., M-2; i = 0, ..., M-1
            where (tau[s, m], tau[s, m+1] = (LOWER, UPPER) limits of m-th response interval
        d_tau[..., 0, :] = d_tau[..., -1, :] = 0.; for extreme limits at +-inf
        d_tau.shape == (N, M+1, M); (N, M) = log_w

    2021-10-31, tested OK
    """
    w = np.exp(log_w)
    # (n_samples, nw) = w.shape
    nw = w.shape[-1]
    cum_w = np.cumsum(w, axis=-1)
    cw = cum_w[..., :-1, np.newaxis]  # only inner limits
    sw = cum_w[..., -1:, np.newaxis]
    # tau[..., m+1] = ln cw[..., m]  - ln (sw[..., 0] - cw[..., m])
    # dcw_dw[..., m, i] = dcw[..., m] / dw[..., i]  = 1. if i <= m else 0.
    dcw_dw = np.tril(np.ones((nw - 1, nw), dtype=int))
    dtau_dw = dcw_dw / cw - (1 - dcw_dw) / (sw - cw)
    dtau_dlogw = dtau_dw * w[..., np.newaxis, :]
    # z_shape = (n_samples, 1, nw)
    # z_shape = (n_samples, 1, nw)
    z_shape = list(dtau_dlogw.shape)
    z_shape[-2] = 1
    return np.concatenate((np.zeros(z_shape),  # *** use np.pad ???
                           dtau_dlogw,
                           np.zeros(z_shape)), axis=-2)


# ---------------------------------------- private help function:
def _check_effects(emf, effects):
    """Check that all effects refer to unique scenario keys
    :param emf: ema_data.EmaFrame instance
    :param effects: iterable with regression-effect specifications
        effects[i] = single key in emf.scenarios.keys(), OR tuple of such keys
    :return: None
    Result: raise RuntimeError if incorrect effects
    """
    effect_keys = sum((list(e_i) if type(e_i) is tuple else [e_i]
                      for e_i in effects), start=[])
    if len(set(effect_keys)) != len(effect_keys):
        raise RuntimeError('scenario keys can occur only ONCE in regression effects')
    # *** Check no effect of scenario dimension with only ONE category
    for e_i in effect_keys:
        if e_i not in emf.scenarios.keys():
            raise RuntimeError(f'regression effect key {e_i} is not a scenario key')


def _make_slices(lengths, start=0):
    """Create a sequence of consecutive index slices, with given lengths
    :param lengths: sequence with desired slice sizes
    :param start: (optional) start index of first slice
    :return: slice_list; len(slice_list) == len(l)
    """
    slice_list = []
    for l_i in lengths:
        slice_list.append(slice(start, start + l_i))
        start += l_i
    return slice_list


def _theta_map(emf, effects):
    """Create 2D array for extraction of attribute locations
    from parameter vector samples
    :param emf: ema_data.EmaFrame instance,
        defining the analysis model structure.
    :param effects: iterable with regression-effect specifications
        effects[i] = tuple with one or more key(s) from emf.scenarios.keys()
    :return: th = 2D binary array, with
        th[j, k] = 1, IFF parameter
        beta[:, j] = xi[:, attr_slice][:, j]
        is the regression effect of k-th <=> (k0, k1, ...)-th scenario on attribute location theta,
        and xi is a 2D array of row parameter-vector samples.
    """
    def theta_one(effect):
        """Make theta_map part for ONE effect term
        :param effect: tuple of one or more scenario keys
        :return: mD array th, with
            th[j, k0, k1, ...] = j-th effect given (k0, k1, ...)-th scenario
            th[j, 0, 0, ...] = 0, in 0-th reference scenario.
            th.shape == (size_effect, *emf.scenario_shape), where
            size_effect = size of category array defined by effect.
        """
        beta_shape = tuple(len(emf.scenarios[sc_i]) for sc_i in effect)
        # = scenario_shape, for this effect term
        beta_ndim = len(beta_shape)
        beta_size = int(np.prod(beta_shape, dtype=int))
        t = np.eye(beta_size).reshape((beta_size, *beta_shape))
        # if effect == effects[0]:  # **** NOT only effects[0] ??? ****
        #     t = t[1:]
            # first effect element of first effect is NOT included in parameter vector
            # because theta == 0 for this reference scenario
            # *** Other method: allow some limited variance also for this reference ???
        t = t[1:]
        # *** fixed theta == 0 for first category in ALL effect terms
        # expand t.ndim to emf.scenario.ndim:
        t = t.reshape(t.shape + tuple(np.ones(len(emf.scenarios) - beta_ndim,
                                              dtype=int)
                                      ))
        ax_0 = range(1, 1 + len(beta_shape))
        ax_new = tuple(list(emf.scenarios).index(e_i) + 1
                       for e_i in effect)
        t = np.moveaxis(t, ax_0, ax_new)
        return t + np.zeros(emf.scenario_shape)
    # ---------------------------------------------------------------
    th = np.concatenate([theta_one(e_tuple)
                         for e_tuple in effects],
                        axis=0)
    return th.reshape((th.shape[0], -1))  # keep as 2D for simplicity

# def _tau_inv(tau):  # ****** Not needed? ****
#     """Inverse of tau()
#     :param tau: 1D or 2D array tau, with all elements in (-inf, +inf]
#         tau[..., m] = UPPER limit for m-th interval,
#             = LOWER limit for the (m+1)-th interval,
#     :return: log_w: 1D or 2D array with
#         log_w[..., m] = ...-th sample of log non-normalized width of m-th interval.
#         log_w.shape[-1] == M == number of response-scale intervals.
#     Method:
#         Normalized widths and interval limits are defined in transformed domain (0, 1.),
#         using a logistic mapping function,
#         y = expit(tau), where y in (0, 1]
#             y[..., m] =  (w_0 +...+ w_m) / (w_0 + ... + w_{M-1};  0 <= m <= M-1
#             w_m = exp(log_w[..., m])
#     """
#     y = expit(tau)
#     # = UPPER interval limits in transformed domain (0, 1.)
#     if y.ndim == 1:
#         y = np.concatenate(([0.], y))
#     else:
#         y = np.concatenate((np.zeros(y.shape[:-1], 1),
#                             y), axis=-1)
#     w = np.diff(y, axis=-1)
#     return np.log(w)


# ------------------------------------------------- TEST:
if __name__ == '__main__':
    from scipy.optimize import approx_fprime, check_grad

    from ema_data import EmaFrame
    from ema_latent import Bradley

    print('*** Testing some ema_base module functions ')
    emf = EmaFrame(scenarios={'CoSS': [f'{i}.' for i in range(1, 8)],
                              'Viktigt': ('Lite',
                                          'Ganska',
                                          'Mycket'),
                              # 'Test': (None, None),
                              'HA': ('A', 'B')
                              },  # nominal variables
                   # stage_key='Stage',
                   attribute_grades={'Speech': ('Svårt',
                                                'Normalt',
                                                'Lätt'),
                                     'Quality': ('Bad', 'Good')
                                     },  # ordinal variables
                   )

    # print('emf=\n', emf)

    main_theta = {'Stage': [0.],
                  'CoSS': 0.1 * np.arange(len(emf.scenarios['CoSS'])),
                  'Viktigt': np.array([-1., 0., 1.]),
                  'HA': np.array([0., 1.])
                  }
    # = only main effects, additive
    regr_effects = ['HA', ('CoSS', 'Viktigt')]

    # effect_HA = np.array([-1., 1.])
    # effect_CoSS = 0.1 * np.arange(len(emf.scenarios['CoSS']))
    # effect_Vikt = np.array([-1., 0., 1.])
    true_theta = main_theta['CoSS'][:, None] + main_theta['Viktigt']
    true_theta = true_theta[..., None] + main_theta['HA']
    true_theta = true_theta[None, ...]  # only one stage
    # stored like emf.scenarios

    beta_HA = main_theta['HA'][1:] - main_theta['HA'][0]
    # beta_CoSS = effect_CoSS[1:] - effect_CoSS[0]
    # beta_Vikt = effect_Vikt[1:] - effect_Vikt[0]
    beta_CoSS_Vikt = main_theta['CoSS'][:, None] + main_theta['Viktigt']
    beta_all = np.concatenate((beta_HA, beta_CoSS_Vikt.reshape((-1)), ))

    eta = [np.zeros(len(r_cat))
           for r_cat in emf.attribute_grades.values()]

    lp_scenarios = np.zeros(emf.scenario_shape).reshape((-1))
    beta_eta = [np.concatenate((beta_all, eta_r))
                for eta_r in eta]
    print(f'len(beta_eta): ', [len(be_i) for be_i in beta_eta])

    xi = np.concatenate((lp_scenarios, *beta_eta))
    xi = xi[None, :]

    # p_base = PopulationMixtureBase()
    p_base = PopulationMixtureBase.initialize(5, emf, regr_effects, rv_class=Bradley)
    print('p_base= ', p_base)
    print(f'p_base.emf=\n{p_base.emf}')
    print(f'p_base.effects= {p_base.effects}')
    print('p_base.scenario_slices', p_base.scenario_slices)
    print('p_base.attribute_slices', p_base.attribute_slices)
    print('p_base.n_parameters= ', p_base.n_parameters)
    print('p_base.n_beta= ', p_base.n_beta)
    print('p_base.theta_map.shape= ', p_base.theta_map.shape)
    print('p_base.comp_prior= ', p_base.comp_prior)

    print('\n*** Testing param extraction methods ***')

    for (stage, alpha_slice) in zip(emf.scenarios[emf.stage_key], p_base.scenario_slices):
        print(f'{emf.stage_key}= {stage}: xi[:, alpha_slice].shape= ', xi[:, alpha_slice].shape)
    # for (stage, alpha) in zip(emf.scenarios[emf.stage_key], p_base.scenario_logprob(xi)):
    #     print(f'{emf.stage_key}= {stage}: prob-mass=\n', np.exp(alpha))
    print(f'\nemf.scenario_shape= {emf.scenario_shape}')
    for (a, a_slice) in zip(emf.attribute_grades.keys(), p_base.attribute_slices):
        print(f'\nAttribute {a}.slice: {a_slice}')
        print(f'\nAttribute {a}: xi[:, a_slice]={xi[:, a_slice]}')

    for a in emf.attribute_grades.keys():
        theta = p_base.attribute_theta(xi, a)
        print(f'\nAttribute {a}: theta.shape={theta.shape}.')
        sc_dim_0 = 'Stage'
        sc_dim_1 = 'CoSS'
        theta = theta.reshape((-1, *emf.scenario_shape))  # *** just for testing
        for (sc_0, theta_0, true_theta_0) in zip(emf.scenarios[sc_dim_0],
                                                 theta[0], true_theta):
            print(f'\t{sc_dim_0}= {sc_0}:')
            for (sc_1, theta_1, true_theta_1) in zip(emf.scenarios[sc_dim_1],
                                                     theta_0, true_theta_0):
                print(f'\t\t{sc_dim_1}= {sc_1}: theta=\n', theta_1)
                print(f'\t\t{sc_dim_1}= {sc_1}: true_theta=\n', true_theta_1)

    for a in emf.attribute_grades.keys():
        tau = p_base.attribute_tau(xi, a)
        print(f'\nAttribute {a}: tau.shape={tau.shape}. tau=\n', tau)

    print('\n*** Testing gradient functions ***')
    print('\n*** Testing p_base._d_tau:')

    eta = np.arange(4)
    limit = 3

    def fun(eta):
        return response_thresholds(eta.reshape((1, -1)))[0, limit]

    def jac(eta):
        return d_response_thresholds(eta.reshape((1, -1)))[0, limit]

    print(f'tau(eta) = {response_thresholds(eta.reshape((1, -1)))}')
    print(f'tau(eta+d) = {response_thresholds(eta.reshape((1, -1)) + .1)} Should remain the same')

    print('approx gradient = ', approx_fprime(eta, fun, epsilon=1e-6))
    print('exact  gradient = ', jac(eta))
    err = check_grad(fun, jac, eta, epsilon=1e-6)
    print('check_grad err = ', err)

