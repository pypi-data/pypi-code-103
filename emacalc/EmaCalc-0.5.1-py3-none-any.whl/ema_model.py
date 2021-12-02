"""This module defines classes for a Bayesian probabilistic model of EMA data.
The model is learned using observed EMA recordings from all subjects,
stored in an ema_data.EmaDataSet instance.

This model version uses a mixture of Gaussian distributions
for the parameter vectors in each sub-population of respondents,
represented by one group of subjects,
with different mixture weights for each sub-population.

Individual parameter distributions are approximated by sampling.
The sub-population mixture model is prior for all individuals in the group.

The model can NOT use Bayesian sequential learning.
It must be trained in a single run from a single batch of EMA data,
which is usually quite sufficient for practical applications.
However, the learn(...) method can be called several times, if needed.

*** Class Overview:

EmaModel: Defines posterior distributions of scenario probabilities,
    and locations of latent variables for perceptual attribute(s),
    learned from EMA data in an ema_data.EmaDataSet instance.
    Includes a GroupModel instance for each sub-population / participant group.

GroupModel: Container for all individual response-probability models,
    defined by an IndividualModel instance for each subject,
    in ONE group of test subjects, assumed recruited from ONE sub-population.

IndividualModel: Distribution of individual parameter vector
    assumed to determine the observed EMA data for ONE subject,
    including, in each EMA record,
    (1) a nominal (possibly multi-dimensional) Scenario, and
    (2) ordinal Ratings for zero, one, or more subjective Attributes.


*** Model Theory: The present model is theoretically similar to
the PairedCompCalc, partly described in
A. Leijon, M. Dahlquist, and K. Smeds (2019):
Bayesian analysis of paired-comparison sound quality ratings. JASA 146(5):3174–3183.

EXCEPT for the present use of a mixture model for the total population.

Detailed math documentation is presented in
A Leijon (2021):
Analysis of EMA Data with Application to
Common Sound Scenarios of Hearing-aid Users
Tech Report 2021-11-xx

*** Version History:
2021-11-03, first functional version
2021-11-04, removed GroupModel.initialize_weights and IndividualModel.initialize_weights
2021-11-05, Hamiltonian sampler -> IndividualModel property -> better stepsize optimization
2021-11-07, store PopulationMixtureBase object as property, so it gets pickled automatically
2021-11-18, cleanup comments
"""
import datetime as dt
import logging

import numpy as np
from scipy.optimize import minimize
from scipy.special import logit, logsumexp, softmax  # , expit

from samppy import hamiltonian_sampler as ham
from samppy.sample_entropy import entropy_nn_approx as entropy

from .dirichlet_point import DirichletVector
from .dirichlet_point import JEFFREYS_CONC
# = Jeffreys prior concentration for Dirichlet distribution

from .ema_base import PopulationMixtureBase, PRIOR_PARAM_SCALE
# = superclass for all model components
from .ema_base import response_thresholds, d_response_thresholds
from .ema_latent import Bradley

# -------------------------------------------------------------------
__version__ = "2021-11-18"

PRIOR_MIXTURE_CONC = JEFFREYS_CONC
# = prior conc for group mixture weights.
# = 0.001 often underestimates sub-population range  ******* Check!
# = 0.5 = Jeffreys prior may over-estimate population range, if few subjects in a group *** Check

DITHER_PARAM_SCALE = 0.1 * PRIOR_PARAM_SCALE  # 0.01 ?
# = initial dithering of point-estimated individual parameters

N_SAMPLES = 1000
# = number of parameter vector samples in each IndividualModel instance

RNG = np.random.default_rng()
# = default module-global random generator

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST
# ham.logger.setLevel(logging.DEBUG)  # *** TEST


# ------------------------------------------------------------------
class EmaModel:
    """Defines probability distributions of EMA recordings
    for all sub-populations from which subjects were recruited,
    and for all subjects in each group,
    given all included EMA data,
    as collected in one ema_data.EmaDataSet instance.

    Model parameters define estimated probabilities for nominal SCENARIOS,
    and estimated latent sensory variables that determine ordinal subjective ratings
    on given ATTRIBUTE questions.
    The sensory variables have continuous values on an INTERVAL scale, as defined by the model,
    although all subjective ratings are discrete on ORDINAL scales.

    The ATTRIBUTE sensory variables may depend on the scenario,
    as estimated by an ordinal regression model,
    including main and interaction effects as requested by the user.

    The model allows for the possibility that different respondents
    might interpret and use the ordinal rating scales in different ways.
    """
    def __init__(self, base, groups):
        """
        :param base: single common PopulationMixtureBase object, used by all model parts
        :param groups: dict with GroupModel instances, stored as
            groups[group] = one GroupModel instance, where
                group = dict key = tuple of tuple(s) = (group_factor, factor_category)
            groups[group].subjects[s_id] = an IndividualModel instance, where
            s_id is a key identifying the subject.
        """
        self.base = base
        self.groups = groups
        self._init_comp()

    def __repr__(self):
        return self.__class__.__name__ + '(groups=groups)'

    @classmethod
    def initialize(cls, ds, effects, max_n_comp=None, rv_class=Bradley):
        """Create a crude initial model from all available count-profile data.
        :param ds: a single ema_data.EmaDataSet instance with all EMA data for analysis
        :param effects: iterable with desired estimated effects of scenario on attribute attribute_grades.
            Each effect element = a key in ds.emf.scenarios, or a tuple of such keys.
        :param max_n_comp: (optional) max number of profile clusters in learned model
            = max number of mixture components in the model
            The number of actually used components may be reduced during VI learning.
        :param rv_class: (optional) class of latent sensory random variable
        :return: a cls instance
        """
        ds.ensure_complete()
        # ensure that data set has sufficiently complete data

        n_subjects = sum(len(g) for g in ds.groups.values())
        if max_n_comp is None:
            max_n_comp = n_subjects // 2
        else:
            max_n_comp = min(n_subjects // 2, max_n_comp)
        base = PopulationMixtureBase.initialize(max_n_comp, ds.emf, effects, rv_class)
        # initialized all base variables, to be used by all model objects
        groups = {g: GroupModel.initialize(base, g_data)
                  for (g, g_data) in ds.groups.items()}
        return cls(base, groups)

    # ------------------------------------------ General VI learn algorithm:
    def learn(self,
              min_iter=10,
              min_step=0.1,
              max_iter=100,
              max_hours=0,
              max_minutes=10,
              callback=None):
        """Learn all individual and population parameter distributions
        from all observed EMA data stored in self.groups[...].subjects[...],
        using Variational Inference (VI).

        This method adapts Gaussian distributions for all mixture components in self.base.comp,
        and Dirichlet distributions for GMM mixture weights in all GroupModel instances,
        and a sampled approximation of parameter distribution in all IndividualModel instances.

        VI maximizes a lower bound to the total likelihood of all observed data.
        The resulting sequence of likelihood values is guaranteed to be non-decreasing,
        except for minor random variations caused by the sampling.

        :param min_iter: (optional) minimum number of learning iterations
        :param min_step: (optional) minimum data log-likelihood improvement,
                 over the latest min_iter iterations,
                 for learning iterations to continue.
        :param max_iter: (optional) maximum number of iterations, regardless of result.
        :param max_hours = (optional) maximal allowed running time, regardless of result.
        :param max_minutes = (optional) maximal allowed running time, regardless of result.
        :param callback: (optional) function to be called after each iteration step.
            If callable, called as callback(self, log_prob)
            where log_prob == scalar last achieved value of VI log-likelihood lower bound
        :return: log_prob = list of log-likelihood values, one for each iteration.

        Result: updated properties of self.base.comp[...], self.groups[...], and
        self.groups[...].subjects[...].xi = parameter sample array, and
        self.groups[...].subjects[...].w = mean mixture weight for the indivicual
        """
        min_iter = np.max([min_iter, 1])
        end_time = dt.datetime.now() + dt.timedelta(hours=max_hours,
                                                    minutes=max_minutes)
        # last allowed time to start new VI iteration
        log_prob = []
        while (len(log_prob) <= min_iter
               or (log_prob[-1] - log_prob[-1 - min_iter] > min_step
                   and (len(log_prob) < max_iter)
                   and (dt.datetime.now() < end_time))):
            log_prob.append(self.adapt())
            if callable(callback):
                callback(self, log_prob[-1])
            logger.info(f'Done {len(log_prob)} iterations. LL={log_prob[-1]:.2f}')
        if dt.datetime.now() >= end_time:
            logger.warning('Learning stopped at time limit, possibly not converged')
        if len(log_prob) >= max_iter:
            logger.warning('Learning stopped at max iterations, possibly not converged')
        return log_prob

    def prune(self, min_weight=JEFFREYS_CONC + 0.01):
        """Prune model to keep only active profile clusters
        :param min_weight: scalar, smallest accepted value for sum individual weight
        :return: None
        Result: all model components pruned consistently
        """
        w_sum = np.sum([np.sum([s.w for s in g.subjects.values()],
                               axis=0, keepdims=False)
                        for g in self.groups.values()],
                       axis=0, keepdims=False)
        # = sum of mixture weights across all subjects in all groups
        keep = w_sum > min_weight
        logger.debug('Before pruning: w_sum = '
                     + np.array2string(w_sum, precision=2, suppress_small=True))
        if np.any(np.logical_and(min_weight < w_sum, w_sum <= 1.5)):
            logger.warning('*** Some component(s) with only ONE member.')
        logger.info(f'Model pruned to {np.sum(keep)} active cluster(s) out of initially {len(keep)}')
        del_index = list(np.arange(len(keep), dtype=int)[np.logical_not(keep)])
        del_index.reverse()
        # Must delete in reverse index order to avoid IndexError
        for i in del_index:
            del self.base.comp[i]
        for g_model in self.groups.values():
            g_model.prune(keep)

    def adapt(self):
        """One adaptation step for all model parameters
        :return: ll = scalar VI lower bound to data log-likelihood,
            incl. negative contributions for parameter KLdiv re priors

        NOTE: All contributions to VI log-likelihood
        are calculated AFTER all updates of factorized parameter distributions
        because all must use the SAME parameter distribution
        """
        # Adapt group mix_weight objects and all subject weights, in each group:
        ll_weights = sum(g.adapt_weights()
                         for g in self.groups.values())
        # ll_weights = - sum_g KLdiv{ q(g.mixweight) || prior.mixweight}
        #       - sum_s KLdiv (q(s.zeta) || prior p(zeta | g.mixweight)}
        for (g, g_model) in self.groups.items():
            logger.debug(f'Adapted Group {g}.mix_weight.alpha= '
                         + np.array2string(g_model.mix_weight.alpha,
                                           precision=4,
                                           suppress_small=True))

        ll_comp = self._adapt_comp()
        # ll_comp = sum_m -KLdiv(current q(mu_m, Lambda_m) || prior(mu_m, Lambda_m)), for
        # q = new adapted model, p = prior model, for m-th mixture component
        # Leijon report eq:CalcLL

        ll_xi = sum(sum(s.adapt_xi()
                        for s in g.subjects.values())
                    for g in self.groups.values())
        #  all ll contributions now calculated using the current updated distributions
        return ll_comp + ll_weights + ll_xi

    def _adapt_comp(self):
        """One VI update for all GMM components in self.base.comp
        :return: ll = sum_m (-KLdiv re prior) across self.base.comp[m]
        """
        w = np.concatenate([[s.w
                             for s in g.subjects.values()]
                            for g in self.groups.values()],
                           axis=0)
        # w[n, c] = weight of c-th component for n-th subject
        xi = np.concatenate([[np.mean(s.xi, axis=0)
                              for s in g.subjects.values()]
                             for g in self.groups.values()],
                            axis=0)
        # xi[n, :] = mean param vector for n-th subject
        xi2 = np.concatenate([[np.mean(s.xi**2, axis=0)
                               for s in g.subjects.values()]
                              for g in self.groups.values()],
                             axis=0)
        # xi2[n, :] = mean squared param vector for n-th subject

        ll = [c.adapt(xi, xi2, w_c, prior=self.base.comp_prior)
              for (c, w_c) in zip(self.base.comp, w.T)]
        # = list of -KLdiv(comp[c] || comp_prior)
        # remaining contributions to total LL calculated later, by IndividualModels
        sum_ll = sum(ll_i for ll_i in ll)
        logger.debug(f'Comp -KLdiv= {sum_ll:.3f} = sum '
                     + np.array2string(np.array(ll),
                                       precision=3, suppress_small=True))
        return sum_ll

    def _init_comp(self):
        """Initialize mixture components to make them clearly separated,
        using only initialized values for all subject.xi.
        :return: None

        Method: pull self.base.comp elements apart by random method like kmeans++
        that tends to maximize separation between components.
        Mixture weights will be adapted later, by GroupModel.adapt_weights
        """
        def distance(x, c):
            """Square-distance from given samples to ONE mixture component,
            as estimated by component logpdf.
            :param x: 2D array of sample row vectors that might be drawn from c
            :param c: one mixture component in self.base.comp
            :return: d = 1D array with non-negative distance measures
                d[n] = distance from x[n] to c
                d.shape == x.shape[0]
            """
            d = - c.mean_logpdf(x)
            return d - np.amin(d)

        def weight_by_dist(d):
            """Crude weight vector estimated from given distance measures
            :param d: 1D array with non-negative distances
            :return: w = 1D array with weights,
                with ONE large element randomly chosen with probability prop.to d2,
                and all other elements small and equal.
                w.shape == d.shape
            """
            w = np.full_like(d, 1. / len(d))
            # ALL samples jointly contribute with weight equiv to ONE sample
            i = np.random.choice(len(d), p=d / sum(d))
            w[i] = len(d) / len(self.base.comp)
            # total weight of all samples divided uniformly across components
            # placed on the single selected i-th sample point
            return w

        # --------------------------------------------------------
        xi = np.concatenate([[np.mean(s_model.xi, axis=0)
                              for s_model in g_model.subjects.values()]
                             for g_model in self.groups.values()], axis=0)
        xi2 = np.concatenate([[np.mean(s_model.xi ** 2, axis=0)
                               for s_model in g_model.subjects.values()]
                              for g_model in self.groups.values()], axis=0)
        xi_d = np.full(len(xi), np.finfo(float).max / len(xi) / 2)
        # = very large numbers that can still be normalized to sum == 1.
        for c_i in self.base.comp:
            c_i.adapt(xi, xi2, w=weight_by_dist(xi_d), prior=self.base.comp_prior)
            xi_d = np.minimum(xi_d, distance(xi, c_i))
            # xi_d[n] = MIN distance from xi[n] to ALL already initialized components


# -------------------------------------------------------------------
class GroupModel:
    """Container for IndividualModel instances
    for all test subjects in ONE group of respondents,
    and a Dirichlet distribution of mixture weights common for the group,
    representing the corresponding sub-population of subjects.
    """
    def __init__(self, base, subjects, mix_weight):
        """
        :param base: single common PopulationMixtureBase object, used by all model parts
        :param subjects: dict with (subject_id, IndividualModel) elements
        :param mix_weight: a single MixtureWeight(DirichletVector) instance,
            with one element for each element of base.comp
        """
        self.base = base
        self.subjects = subjects
        self.mix_weight = mix_weight

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                f'\n\tsubjects= {len(self.subjects)} individuals,' +
                f'\n\tmix_weight={repr(self.mix_weight)})')

    @classmethod
    def initialize(cls, base, group_data):
        """Crude initial group model given group EMA data
        :param base: single common PopulationMixtureBase object, used by all model parts
        :param group_data: a dict with elements (s_id, s_ema), where
            s_id = a subject key,
            s_ema = list with EMA records from an ema_data.EmaDataSet object.
            Each record is a dict with elements (key, category), where
            key can be one of either Scenarios or Ratings keys, and
            category = the recorded response
        :return: a cls instance crudely initialized
        """
        s_models = {s_id: IndividualModel.initialize(base, s_ema)
                    for (s_id, s_ema) in group_data.items()}
        mix_weight = MixtureWeight.initialize(x=np.mean([s.w
                                                         for s in s_models.values()],
                                                        axis=0))
        return cls(base, s_models, mix_weight)

    def adapt_weights(self):
        """One update step of properties self.mix_weight,
        and mixture weights and parameter distributions
        for all group member subjects
        :return: ll = - KLdiv(self.mix_weight || prior.mix_weight), after updated mix_weight
            - sum_s KLdiv( q(zeta_s || prior(zeta_s) ), after updated q(zeta_s)
            + sum_s E{ log p(data_s, xi_s| model) / q(xi_s) },
            across all s-th subjects in self

        NOTE: total log-likelihood calculated AFTER current VI update
        """
        self.mix_weight.alpha = (np.sum([s.w
                                         for s in self.subjects.values()],
                                        axis=0)
                                 + PRIOR_MIXTURE_CONC)
        # = Leijon tech report eq:UpdateV

        prior_alpha = PRIOR_MIXTURE_CONC * np.ones(len(self.base.comp))
        neg_kl_v = - self.mix_weight.relative_entropy(DirichletVector(alpha=prior_alpha))
        # neg_kl_v = - E_q{ ln q(v_g) / p(v_g) } for self

        w_mean_log = self.mix_weight.mean_log
        neg_kl_zeta = sum(s.adapt_weights(w_mean_log)
                          for s in self.subjects.values())
        # = - sum_s E{ ln q(zeta_s) / prior(zeta_s) }
        logger.debug(f'Group -KL_mix= {neg_kl_v:.3f}.')
        return neg_kl_zeta + neg_kl_v

    def prune(self, keep):
        """Prune model to keep only active profile clusters
        :param keep: boolean index array for components to keep
        :return: None

        Result: model properties pruned consistently
        """
        self.mix_weight.alpha = self.mix_weight.alpha[keep]
        for s_model in self.subjects.values():
            s_model.prune(keep)

    def predictive_population_ind(self):
        """Predictive probability-distribution for
        sub-population represented by self
        :return: a ProfileMixtureModel object

        Method: report eq:PredictiveSubPopulation
        """
        comp = [c_m.predictive for c_m in self.base.comp]
        return ProfileMixtureModel(self.base, comp, self.mix_weight.mean)

    def predictive_population_mean(self):
        """Predictive probability-distribution for MEAN parameter vector
        in sub-population represented by self
        :return: a ProfileMixtureModel object

        Method: report eq:PredictiveSubPopulation
        """
        comp = [c_m.mean.predictive for c_m in self.base.comp]
        return ProfileMixtureModel(self.base, comp, self.mix_weight.mean)


# -------------------------------------------------------------------
class IndividualModel:
    """Container for EMA response data for ONE respondent,
    and a sampled approximation of the individual parameter distribution,
    and mixture weights for the parameters.

    The mixture weights and superclass list of mixture components
    define a hierarchical prior distribution for the individual parameters.

    Individual parameter distributions are approximated by a large set of samples
    stored as property xi, with
    self.xi[s, :] = s-th sample vector of parameters,
    with subsets of parameter types (alpha, beta, eta) as defined by self.base.
    """
    def __init__(self, base, scenario_count, rating_count, xi, w):
        """
        :param base: single common PopulationMixtureBase object, used by all model parts
        :param scenario_count: 2D array with response counts
            scenario_count[k0, k] = number of responses
            in k-th <=> (k1, k2, ...)-th scenario category at k0-th test stage,
            using flattened index for scenario dimensions 1,2,....
            NOTE: ema_data.EmaFrame always stores test stage as first scenario dimension.
        :param rating_count: list of 2D arrays with response counts
            rating_count[i][l, k] = number of responses for i-th ATTRIBUTE,
            at l-th ordinal level, given the k-th <=> (k0, k1, k2, ...)-th scenario
        :param xi: 2D array with parameter sample vector(s)
            xi[s, j] = s-th sample of j-th individual parameter,
                concatenating parameter sub-types as defined in superclass.
        :param w: 1D array with non-negative elements
            w[m] = E{ Prob(ALL self.xi generated by self.base.comp[m]) }
            np.sum(w) == 1.
            len(w) == len(self.base.comp)
        """
        self.base = base
        self.scenario_count = scenario_count
        self.rating_count = rating_count
        self.xi = xi
        self.w = w
        self._sampler = ham.HamiltonianSampler(x=self.xi,
                                               fun=self._neg_ll,  # ***** static method ?
                                               jac=self._grad_neg_ll,
                                               epsilon=0.2,
                                               n_leapfrog_steps=10,     # = default
                                               min_accept_rate=0.8,     # = default
                                               max_accept_rate=0.95,    # = default
                                               rng=RNG
                                               )
        # keeping sampler properties across learning iterations

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\tscenario_count=' + f'{self.scenario_count},' +
                '\n\trating_count=' + f'{self.rating_count},' +
                '\n\txi= array with shape' + f' {self.xi.shape} parameter samples,' +
                f'\n\tw= ' + np.array_str(self.w,
                                          precision=4, suppress_small=True))

    @classmethod
    def initialize(cls, base, ema_data):
        """Create model from recorded data
        :param base: single common PopulationMixtureBase object, used by all model parts
        :param ema_data: list of ema tuples, as stored im ema_data.EmaDataSet instance
        :return: a cls instance
        """
        z = _count_scenarios(ema_data, base.emf)
        # z[t, k] = number of EMA assessments at t-th test stage
        # in k-th <=> (k1, k2, ...)-th scenario, EXCL. k0= test stage
        y = _count_ratings(ema_data, base.emf)
        # y[i][l, k] = number of attribute_grades at l-th ordinal level for i-th ATTRIBUTE question
        # given k-th <=> (k0, k1, k2, ...)-th scenario (INCL. k0= test stage)
        alpha = _initialize_scenario_param(z)
        xi = list(np.ravel(alpha))
        for y_i in y:
            theta = _initialize_rating_theta(y_i).reshape(-1)
            a = base.theta_map.reshape((base.theta_map.shape[0], -1))  # **** needed ?
            beta = np.linalg.lstsq(a.T, theta, rcond=None)[0]
            eta = np.zeros(len(y_i))
            xi.extend(np.concatenate((beta, eta)))
        xi = np.array(xi)
        # dither to N_SAMPLES:
        xi = xi + DITHER_PARAM_SCALE * RNG.normal(size=(N_SAMPLES, len(xi)))
        w = np.ones(len(base.comp)) / len(base.comp)  # uniform distribution
        return cls(base, z, y, xi, w)

    def adapt_weights(self, prior_mean_log_v):
        """Adapt mixture weights
        :param prior_mean_log_v: 1D vector with
            prior_mean_log_v[c] = mean log sub-population weight for c-th mixture component
        :return: scalar KL = - KLdiv{ q(zeta) || prior_p(zeta)}
            = - E_zeta { ln q(zeta) / prior_p(zeta)}, where
            self.w = E{ zeta } = expectation of 1-of-M binary component selector.
            q(zeta) = prod_c self.w[c]**zeta_c; categorical discrete distribution
            prior_p(zeta | group.mix_weight) = prod_c v_c^{zeta_c}
            ln prior_p(zeta | group.mix_weight) = zeta * prior_mean_log_v  ***** ????????
        Result: Updated self.w
        """
        ln_r = np.array([np.mean(c.mean_logpdf(self.xi))
                         for c in self.base.comp]) + prior_mean_log_v
        ln_r -= np.amax(ln_r)  # just to avoid underflow in exp
        self.w = np.exp(ln_r)
        self.w /= np.sum(self.w)
        return - np.dot(self.w, np.log(self.w) - prior_mean_log_v)

    def adapt_xi(self):
        """Adapt parameter distribution self.xi
        to stored EMA count data, given the current self.w
        and the current estimate of population GMM components self.base.comp.
        :return: scalar LL = VI lower bound of data log-likelihood, given parameters,
            = E{ ln p(self.scenario_count, self.rating_count | self.xi) }
             - E{ ln q(xi) / prior_p(xi) }_q(xi)
        Result: Updated self.xi
        """
        # find MAP point first:
        xi_0 = np.mean(self.xi, axis=0)
        res = minimize(fun=self._neg_ll,  # _1,
                       jac=self._grad_neg_ll,  # _1,
                       x0=xi_0)
        if res.success:
            xi_map = res.x.reshape((1, -1))
        else:
            raise RuntimeError('MAP search did not converge: '
                               + 'res= ' + repr(res))

        if len(self.xi) != N_SAMPLES:
            # run sampler starting from x_map
            self._sampler.x = xi_map
        else:
            # we have sampled before, start from those samples
            self._sampler.x = self.xi + xi_map - xi_0
        self._sampler.safe_sample(n_samples=N_SAMPLES, min_steps=2)
        logger.debug(f'sampler accept_rate = {self._sampler.accept_rate:.1%}, ' +
                     f'n_steps = {self._sampler.n_steps:.0f}, ' +
                     f'epsilon = {self._sampler.epsilon:.2f}')
        self.xi = self._sampler.x
        # **** force eta params to zero mean, no effect on thresholds
        for a_ind in self.base.attribute_slices:
            eta_ind = slice(a_ind.start + self.base.n_beta, a_ind.stop)
            # must change self.xi in place, cannot use 2-step indexing
            eta_mean = np.mean(self.xi[:, eta_ind],
                               axis=-1, keepdims=True)
            self.xi[:, eta_ind] -= eta_mean
        lp_xi = - np.mean(self._sampler.U)
        # lp_xi = E{ ln p(data | xi) + ln prior_p(xi) }_xi
        h_xi = entropy(self.xi)
        # approx = - E{ ln q(xi) }
        return lp_xi + h_xi

    def _neg_ll(self, xi):
        """Objective function for self.adapt_xi
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: neg_ll = scalar or 1D array
            neg_ll[...] = - ln P{ self.scenario_count, self.rating_count | xi[..., :]}
        """
        return - self.prior_logpdf(xi) - self.logprob(xi)

    def _grad_neg_ll(self, xi):
        """Jacobian of self._neg_ll
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: dll = scalar or 1D array
            dll[..., j] = d _neg_ll(xi[..., :]) / d xi[..., j]
            dll.shape == xi.shape
        """
        return - self.d_prior_logpdf(xi) - self.d_logprob(xi)

    def logprob(self, xi):
        """log likelihood of EMA count data, given model parameters
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: ll = scalar or 1D array
            ll[...] = ln P{ self.scenario_count, self.rating_count | xi[..., :]}
        """
        def scenario_logprob(sc_xi):
            """Log probability mass for scenario categories in ONE test stage
            :param sc_xi: 1D or 2D array with model parameters for ONE test stage
                = alpha = log P{scenarios}, NOT necessarily normalized
            :return: lp = 1D or 2D array with
                lp[..., k] = log P{ k-th scenario | sc_xi[..., :] }
                properly normalized, with sum_k exp(lp[:, k]) == 1.
                lp.shape == sc_xi.shape
            """
            return sc_xi - logsumexp(sc_xi, axis=-1, keepdims=True)

        def rating_logprob(a_xi):
            """Log probability mass for rating categories for ONE attribute.
            :param a_xi: 1D or 2D array with model parameters for this attribute
            :return: lp = 2D or 3D array with
                lp[..., l, k] = log P{ l-th ordinal level | k-th scenario, a_xi[..., :] }
            """
            return self.base.rv_class.log_cdf_diff(*self.cdf_args(a_xi))
        # ---------------------------------------------------------------

        ll_z = sum(np.dot(scenario_logprob(xi[..., sc_t]), z_t)
                   for (z_t, sc_t) in zip(self.scenario_count,
                                          self.base.scenario_slices))
        # z_t[k] = k-th scenario count for t-th test stage
        # sc_t = parameter slice for t-th test stage
        ll_y = sum(np.einsum('lk, ...lk -> ...',  # ********* use np.tensordot ???
                             y_i, rating_logprob(xi[..., a_i]))
                   for (y_i, a_i) in zip(self.rating_count,
                                         self.base.attribute_slices))
        # y_i[l, k] = (l, k)-th count for i-th attribute rating
        # a_i = param slice for i-th attribute rating
        return ll_z + ll_y

    def d_logprob(self, xi):
        """Jacobian of self.logprob(xi)
        :param xi: 1D or 2D array with candidate parameter vectors
        :return: d_ll = 2D array
            d_ll[..., j] = d ln P{ self.scenario_count, self.attribute_grades | xi[..., :]} / d xi[..., j]
        """
        def d_scenario_logprob(sc_xi):  # ******** use count input, save RAM ?
            """Gradient of scenario_logprob for ONE test stage
            :param sc_xi: 1D or 2D array with model parameters for ONE test stage
                = alpha = log P{scenarios}, NOT necessarily normalized
            :return: dlp = 2D or 3D array with
                dlp[..., k, j]
                = d log P{ scenario_logprob()[..., k] | sc_xi[..., :] } / d sc_xi[..., j]
            """
            # lp[s, k] = sc_xi[s, k] - ln sum_i(exp(sc_xi[s, i]))
            # dlp[s, k, j] = 1(k==j) - softmax(sc_xi[s, :], axis=-1)[s, j]
            return np.eye(sc_xi.shape[-1]) - softmax(sc_xi[..., None, :], axis=-1)

        # -----------------------------------------------------------------------

        d_ll = [np.einsum('k, ...kj -> ...j',  # ******* use dot or matmul?
                          z_t, d_scenario_logprob(xi[..., sc_t]))
                for (z_t, sc_t) in zip(self.scenario_count,
                                       self.base.scenario_slices)]
        # z_t[k] = k-th count for t-th test stage
        # sc_t = parameter slice for t-th test stage
        for (y_i, a_i) in zip(self.rating_count, self.base.attribute_slices):
            # a_xi = xi[:, a_i]
            a_xi = xi[..., a_i]
            (dlp_low, dlp_high) = self.base.rv_class.d_log_cdf_diff(*self.cdf_args(a_xi))
            # append dlp_d_beta[s, j] = d rating_logprob()[s] / d xi[:, a_i][:, j]
            d_ll.append(np.einsum('...lk, lk, jk -> ...j',
                                  dlp_low + dlp_high, y_i, - self.base.theta_map))  # tensordot 2 steps?
            d_tau_d_eta = d_response_thresholds(a_xi[..., self.base.n_beta:])
            # append dlp_d_eta[..., j] = d rating_logprob()[s] / d xi[:, a_i][:, self.n_beta + j]
            d_ll.append(np.einsum('...lk, lk, ...lj -> ...j',  # *** use dot , matmul
                                  dlp_low, y_i, d_tau_d_eta[..., :-1, :]) +
                        np.einsum('...lk, lk, ...lj -> ...j',
                                  dlp_high, y_i, d_tau_d_eta[..., 1:, :]))
            # all d_ll[i][..., :] elements have matching shapes
        return np.concatenate(d_ll, axis=-1)

    def cdf_args(self, a_xi):
        """Extract arguments for rv_class logprob calculation
        :param a_xi: 1D or 2D array with rating-model sample for given attribute a
            a_xi[..., j] = ...-th sample of j-th rating-model parameter
        :return: tuple (arg_low, arg_high) with 2D or 3D array args for probabilistic model,
            such that
            P[ l-th response | ...-th parameter sample, k-th scenario ] =
            = rv_class.cdf(arg_high[..., l, k]) - rv_class.cdf(arg_low[..., l, k])
        """
        theta = np.dot(a_xi[..., :self.base.n_beta], self.base.theta_map)
        # theta[..., k] = ...-th sample of latent variable, given k-th scenario
        # tau_old = self.base.tau(a_xi[..., self.base.n_beta:])
        tau = response_thresholds(a_xi[..., self.base.n_beta:])
        a = tau[..., :-1, None]  # lower interval limits
        b = tau[..., 1:, None]  # upper interval limits
        return a - theta[..., None, :], b - theta[..., None, :]

    def prior_logpdf(self, xi):
        """prior log pdf of model parameters
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: ll = scalar or 1D array
            ll[...] = ln p{xi[..., :] | self.w, self.base.comp}
        """
        return sum(w_c * c.mean_logpdf(xi)
                   for (w_c, c) in zip(self.w, self.base.comp))

    def d_prior_logpdf(self, xi):
        """gradient of prior_logprob
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: d_ll = 1D or 2D array
            d_ll[..., k] = d ln p{xi[..., :] | self.w, self.base.comp} / d xi[..., k]
        """
        return sum(w_c * c.grad_mean_logpdf(xi)
                   for (w_c, c) in zip(self.w, self.base.comp))

    def prune(self, keep):
        """Prune model to keep only active mixture components
        :param keep: boolean index array for components to keep
        :return: None

        Result: property self.w pruned consistently
        """
        self.w = self.w[keep]
        # re-normalize just in case some small value was lost
        self.w /= np.sum(self.w)

    def rvs(self, size=N_SAMPLES):
        # re-sample if size != len(self.xi) *********************
        return self.xi


# ------------------------------------------------------------------
class ProfileMixtureModel:
    """Help class defining a non-Bayesian predictive model
    for parameter distribution in a sub-population,
    derived from existing trained model components
    """
    def __init__(self, base, comp, w):
        """
        :param base: ref to common PopulationMixtureBase object
        :param comp: list of predictive mixture component models
            NOT same as original base.comp
        :param w: 1D array with mixture weight values
        """
        self.base = base
        self.comp = comp
        self.w = w

    @property
    def mean(self):
        """Mean of parameter vector, given population mixture,
        averaged across mixture components
        and across posterior distribution of component concentration params.
        :return: 1D array
        """
        return np.dot(self.w, [c_m.mean for c_m in self.comp],
                      axes=1)

    def rvs(self, size=N_SAMPLES):
        """Generate random probability-profile samples from self
        :param size: integer number of sample vectors
        :return: xi = 2D array of parameter-vector samples
            xi[s, :] = s-th sample vector, structured as specified by self.base
        """
        n_comp = len(self.comp)
        s = RNG.choice(n_comp, p=self.w, size=size)
        # = array of random comp indices
        ns = [np.sum(s == n) for n in range(n_comp)]
        xi = np.concatenate([c.rvs(size=n_m) for (n_m, c) in zip(ns, self.comp)])
        RNG.shuffle(xi)
        return xi


# -----------------------------------------------------------------
class MixtureWeight(DirichletVector):
    """Non-Bayesian Dirichlet-distributed weight vector for one mixture distribution
    defined by property
    alpha = 1D concentration vector
    """
    @classmethod
    def initialize(cls, x):  # ******************** Move to DirichletVector ???
        """Crude initial setting of concentration parameters
        :param x: array-like 1D list with non-normalized row vector(s)
            that might be generated from a cls instance,
            OR from a multinomial distribution with a cls instance as probability
        :return: a new cls instance
        """
        a = np.array(x) + JEFFREYS_CONC
        # including Jeffreys concentration as pseudo-count
        a /= np.sum(a, axis=-1, keepdims=True)
        a *= JEFFREYS_CONC * a.shape[-1]
        # = normalized with average conc = JEFFREYS_CONC
        return cls(a, rng=RNG)


# --------------------------------------------- module help functions:

def _count_scenarios(ema_data, emf):
    """Encode EMA scenario categories as a scenario_count for analysis
    :param ema_data: list of EMA records for ONE respondent
    :param emf: ema_data.EmaFrame instance
    :return: z = 2D array with scenario_counts
        z[t, k] = number of recorded k-th <=> (k1,...)-th scenario category
        at t-th test-stage
        z.shape == (emf.n_stages, emf.n_scenarios / emf.n_stages
    """
    z = np.zeros(emf.scenario_shape, dtype=int)
    for r in ema_data:
        z[emf.scenario_index(r)] += 1
    return z.reshape((emf.scenario_shape[0], -1))


def _count_ratings(ema_data, emf):
    """Encode EMA ATTRIBUTE attribute_grades as a rating_count list of arrays for analysis
    :param ema_data: list of EMA attribute_grades for ONE respondent
    :param emf: ema_data.EmaFrame instance
    :return: y = list of rating_count arrays,
        y[i][l, k] = number of responses at l-th ordinal level for i-th attribute,
        given the k-th <=> (k0, k1, ...)-th scenario category in the same EMA record
        y[i].shape == (len(emf.attribute_grades[i]), emf.n_scenarios)
    """
    y = [np.zeros((len(r_cat), *emf.scenario_shape), dtype=int)
         for r_cat in emf.attribute_grades.values()]
    for r in ema_data:
        sc_index = emf.scenario_index(r)
        for (i, level_i) in enumerate(emf.rating_index(r)):
            if level_i is not None:  # *** missing attribute_grades are ALLOWED
                y[i][level_i][sc_index] += 1
    for (i, r_cat) in enumerate(emf.attribute_grades.values()):
        y[i] = y[i].reshape((len(r_cat), -1))
    return y


def _initialize_scenario_param(z):
    """Crude initial estimate of scenario logprob parameters
    :param z: array with scenario counts
    :return: alpha = 2D array
        alpha[t, k] = log prob of k-th scenario at t-th test stage
        alpha.shape == (z.shape[0], z[0].size)
    """
    p = z.reshape((z.shape[0], -1)) + JEFFREYS_CONC  # PRIOR_PSEUDO_RESPONDENT
    p /= np.sum(p, axis=-1, keepdims=True)
    return np.log(p)


def _initialize_rating_theta(y):
    """Crude initial estimate of latent sensory variable for ONE attribute question
    :param y: rating_count array,
        y[l, k0, k1, ...] = number of responses at l-th ordinal level,
        given the (k0, k1, ...)-th scenario category
    :return: theta = array of sensory-variable locations
        theta[k0, k1, ...] = estimated location of latent variable,
        given the (k0, k1, ...)-th scenario category
        theta.shape == y[0].shape
    """
    n_levels = y.shape[0]
    expit_th = (np.arange(n_levels) + 0.5) / n_levels
    th = logit(expit_th)
    # back-transformed midpoints in each response interval
    p = y + JEFFREYS_CONC  # PRIOR_PSEUDO_RESPONDENT
    p /= np.sum(p, axis=0, keepdims=True)
    theta = np.tensordot(th, p, axes=1)
    # = typical (midpoint) location, given y
    return theta  # .reshape((theta.shape[0], -1))


# ------------------------------------------------- TEST:
# tested with complete package: run_sim.py, run_ema.py
#
# if __name__ == '__main__':
