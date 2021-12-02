"""This module defines classes and methods for
simulated EMA study with groups of respondents,
drawn at random from population(s) with specified
inter-individual distributions of all model parameters.

The simulations can generate artificial data with exactly the same structure
as that obtained from a real experimental data set.


*** Main Module Classes:

EmaSimPopulation: defines distribution of model parameters
    for probabilities of one or more SCENARIOS, in one or more Scenario Dimensions,
    and one or more perceptual ATTRIBUTE latent-variable locations
    in ONE (sub-)population of subjects.

EmaSimExperiment: defines an EMA experiment,
    generates simulated responses for one or more groups of subjects,
    sampled from EmaSimPopulation instance(s).
    The EMA data layout is defined by an ema_data.EmaFrame instance,
    defining all Scenario dimensions and categories, and
    defining discrete ordinal response scales for each Attribute.

EmaSimSubject = superclass for subject properties

SubjectThurstone: single subject with Attribute ratings determined by
    the Thurstone Case V model, assuming Gaussian latent sensory variable

SubjectBradley: single subject with Attribute ratings determined by
    the Bradley-Terry-Luce (BTL) model, assuming Logistic latent sensory variable

*** Main Class Methods:

EmaSimPopulation.gen_group(...)
    draws a group of simulated subjects at random from the simulated Population.

EmaSimExperiment.gen_dataset(...)
    generates am ema_data.EmaDataSet instance with simulated EMA records
    for one or more groups of simulated subjects.
    All data can be saved to files using the dataset.save(...) method.

*** Usage example: See script run_sim.py

*** Version History:
* Version 0.5.1:
2021-11-25, allow experiment with NO Attributes

* Version 0.5:
2021-11-14, copied and modified PairedCompCalc -> EmaCalc
2021-11-16, first functional version
2021-11-21, rather extensively tested
"""

import numpy as np
# from scipy.stats import randint, uniform, norm
# import itertools
# import copy
import logging

from .ema_data import EmaDataSet
from .ema_base import response_thresholds
from . import ema_latent


RNG = np.random.default_rng()
# = default module-global random generator

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # test


# --------------------------------------- subject response models
class EmaSimSubject:
    """Simulate one individual participant in an EMA data-collection experiment.
    Superclass for either SubjectBradley or SubjectThurstone
    """
    def __init__(self, sc_prob, a_theta, a_tau):  # lapse_prob=0.):
        """
        :param sc_prob: mD array with (non-normalized) conditional Scenario probability
            sc_prob[k0, k1, k2,...] propto Prob (k1, k2, ...)-th scenario, GIVEN k0-th Stage
            sc_prob.shape == emf.scenario_shape
        :param a_theta: dict with (a_key, a_theta) elements,
            a_key is a string identifying ONE Attribute among emf.attribute_grades.keys()
            a_theta[k0, k1, ...] = mD array with mean of latent sensory variable for Attribute a_key,
        :param a_tau: dict with (a_key, thr) elements, where
            tnr[l] = UPPER interval limit for l-th ordinal response,
            NOT including extreme -inf, +inf limits
        """
        self.sc_prob = sc_prob
        self.a_theta = a_theta
        self.a_tau = a_tau

    def __repr__(self):
        return (f'{self.__class__.__name__}(\n\t' +
                ',\n\t'.join(f'{key}={repr(v)}'
                             for (key, v) in vars(self).items()) +
                '\n\t)')

    def gen_ema_records(self, emf, min_ema, max_ema):
        """
        :param emf: ema_data.EmaFrame instance
        :param min_ema: min random number of EMA records per Stage
        :param max_ema: max random number of EMA records per Stage
        :return: ema_list = sequence of dicts with elements (key, cat), where
            key is one of emf.scenarios or emf.attribute_grades, and
            cat is one of the allowed categories for that key
            len(ema_list) == n_records
        """
        def scenario_index(sc_p, sc_shape):
            """Generate ONE random scenario index tuple, NOT including Stage index
            :param sc_p: 1D probability-mass array for all scenarios, EXCEPT Stage
            :param sc_shape: tuple with scenario_shape EXCEPT Stage dimension
            :return: ind = index tuple; len(ind) = len(sc_shape)
             """
            sc_ind = RNG.choice(len(sc_p), p=sc_p)  # linear random index
            return np.unravel_index(sc_ind, shape=sc_shape)

        def scenario_dict(sc_ind):
            """Convert index tuple to Scenario dict
            """
            return {sc_k: sc_cat[i]
                    for (i, (sc_k, sc_cat)) in zip(sc_ind,
                                                   emf.scenarios.items())}
        # -------------------------------------------------------

        ema_list = []
        sc_shape_stage = emf.scenario_shape[1:]
        sc_prob_stage = self.sc_prob.reshape((self.sc_prob.shape[0], -1))
        for (i, p) in enumerate(sc_prob_stage):
            n_rec = RNG.integers(min_ema, max_ema)
            for _ in range(n_rec):
                sc = (i, *scenario_index(p, sc_shape_stage))
                a_grades = self.gen_attr_grades(emf, sc)
                ema_list.append(scenario_dict(sc) | a_grades)
        return ema_list

    def gen_attr_grades(self, emf, sc):  # done by subclass
        """Generate random ordinal Attribute grades in given Scenario
        :param emf: external ema_data.EmaFrame object defining experimental layout
        :param sc: index tuple for scenario of this record
        :return: a_grades = dict with elements (a, grade)
        """
        def rvs_grade(th, tau):  # ****** Done by Bradley ???
            x = self.rvs(th)
            return np.sum(x > tau)
        # -------------------------------------------------------
        return {a: emf.attribute_grades[a][rvs_grade(a_th[sc], self.a_tau[a])]
                for (a, a_th) in self.a_theta.items()}

    @staticmethod
    def rvs(th):
        """Abstract method, implemented by sub-class
        """
        raise NotImplementedError

    # def lapse(self):
    #     """Generate True with prob = self.lapse_prob
    #     """
    #     return uniform.rvs(0, 1.) < self.lapse_prob
    #
    # def lapse_response(self):
    #     """Generate a random result, disregarding quality parameters
    #     :return: scalar integer
    #         in {-n_difference_grades, ...,-1, +1,..., + n_difference_grades}, if forced_choice
    #         in {-n_difference_grades+1, ...,0, ...,  + n_difference_grades-1}, if not forced_choice
    #         i.e., excluding 0 if self.emf.forced_choice
    #     """
    #     n_response_limits = len(self.response_thresholds)
    #     # if self.emf.forced_choice:
    #     if self.response_thresholds[0] == 0.:  # forced_choice
    #         return ((-1 if uniform.rvs() < 0.5 else +1) *
    #                 randint.rvs(low=1, high=n_response_limits + 1))
    #
    #     else:
    #         return randint.rvs(low=-n_response_limits,
    #                            high=n_response_limits + 1)
    #


class SubjectThurstone(ema_latent.Thurstone,
                       EmaSimSubject):
    """Simulate a subject using the Thurstone Case V choice model.
    """
    # @staticmethod
    # def latent_rvs(loc):
    #     return loc + RNG.standard_normal()


class SubjectBradley(ema_latent.Bradley,
                     EmaSimSubject):
    """Simulate one individual participant in a paired-comparison experiment.
    The subject responds using the Bradley-Terry-Luce choice model,
    with parameters defined in the log domain.
    """
    # @staticmethod
    # def rvs(loc):  # *** implemented by ema_latent.Bradley
    #     return loc + RNG.logistic()


# -------------------------------------------------------------------------
class EmaSimPopulation:
    """Defines a simulated population
    from which groups of random test subjects can be generated
    for a simulated EMA experiment.

    The population instance defines distributions for
    one or more nominal Scenario categories, and
    one or more perceptual Attributes, given any Scenario.

    Each Scenario is a combination of one category from each Scenario Dimension.
    """
    def __init__(self, emf,
                 scenario_prob,
                 attribute_mean=None,
                 log_scenario_std=0.,
                 attribute_std=0.,
                 # log_response_width_mean=0.,
                 log_response_width_std=0.,
                 lapse_prob_range=(0., 0.),  # ******* not needed, not used ******
                 subject_class=SubjectBradley,
                 id=''):
        """
        :param emf: ema_data.EmaFrame instance defining Scenarios and Attributes
        :param scenario_prob: array-like multi-dim, with
            scenario_prob[k0, k1,...] prop.to probability of (k1, k2,...)-th scenario,
            GIVEN the k0-th TestStage category, even if only one stage category.
            scenario_prob.shape must correspond to shape of scenarios.
        :param attribute_mean: (optional) dict or iterable with elements (a_key, a_mean), where
            a_key is string id of a rated perceptual attribute,
            a_mean is an mD array with
            a_mean[k0, k1, ...] = latent-variable mean for attribute a_key,
            given the (k0, k1,...)-th Scenario category, i.e.,
            a_mean.shape == scenario_prob.shape, for all attributes.
        :param log_scenario_std: (optional) inter-individual standard deviation of
            log probabilities for each scenario category.
        :param attribute_std: (optional) scalar inter-individual standard deviation of all attribute parameters
        :param log_response_width_std: (optional) scalar standard deviation of log(response-interval-width)
        :param lapse_prob_range: (optional) tuple (min, max) probability of random lapse response
        :param subject_class: (optional) subject probabilistic model for generating responses
        :param id: (optional) string label, used as prefix in all generated subject names
        """
        self.emf = emf
        scenario_prob = np.asarray(scenario_prob)
        if emf.scenario_shape[0] == 1 and emf.scenario_shape[1:] == scenario_prob.shape:
            scenario_prob = scenario_prob[None, ...]
        if emf.scenario_shape != scenario_prob.shape:
            raise RuntimeError('scenario_prob.shape must agree with scenarios')
        self.scenario_prob = scenario_prob
        for (i, sc_i) in enumerate(self.scenario_prob):
            self.scenario_prob[i] /= np.sum(sc_i)  # normalize conditional probabilities, given Stage
        self.log_scenario_std = log_scenario_std

        if attribute_mean is None:
            attribute_mean = dict()
        else:
            attribute_mean = dict(attribute_mean)
        if set(attribute_mean.keys()) != set(emf.attribute_grades.keys()):
            raise RuntimeError('attribute_mean must define same attributes as EmaFrame')
        for (a, a_mean) in attribute_mean.items():
            if (self.emf.scenario_shape[0] == 1
                    and self.emf.scenario_shape[1:] == a_mean.shape):
                # a_mean = a_mean[None, ...]
                attribute_mean[a] = attribute_mean[a][None, ...]
        assert all(a_mean.shape == self.emf.scenario_shape
                   for a_mean in attribute_mean.values()), 'attribute_mean.shape must match scenario_shape'
        self.attribute_mean = attribute_mean
        self.attribute_std = attribute_std
        self.log_response_width_std = log_response_width_std
        self.lapse_prob_range = lapse_prob_range
        self.subject_class = subject_class
        self.id = id

    def __repr__(self):
        return (f'{self.__class__.__name__}(\n\t' +
                ',\n\t'.join(f'{key}={repr(v)}'
                             for (key, v) in vars(self).items()) +
                '\n\t)')

    @property
    def n_attributes(self):
        return len(self.attribute_mean)

    def gen_group(self, n_subjects=1):
        """Create a group of simulated-subject instances randomly drawn from self,
        with properties suitable for a planned experiment.
        :param n_subjects: number of randomly drawn subjects from self
        :return: group_dict = dict with elements (subject, ema_list), where
            ema_list = list with elements ema, where
                ema = tuple with elements (key, value), where
                key is one of [scenario_key, attribute_key],
                value is one allowed category for this key.
                len(ema) = emf.n_variables
        """
        def gen_sc_prob():
            sc_p = np.exp(np.log(self.scenario_prob) +
                          self.log_scenario_std *
                          RNG.standard_normal(size=self.emf.scenario_shape))
            for (i, sc_i) in enumerate(sc_p):
                sc_p[i] /= np.sum(sc_i)  # normalize conditional probabilities, given Stage
            return sc_p

        def gen_attr():
            theta = self.attribute_std * RNG.standard_normal(size=(self.n_attributes,
                                                                   *self.emf.scenario_shape))
            # theta[i, ...] = random offset of location for i-th attribute of s-th subject
            return {a: th_mean + th_d
                    for ((a, th_mean), th_d) in zip(self.attribute_mean.items(),
                                                    theta)}

        def gen_tau():
            """Random tau parameters for each attribute
            """
            return {a: response_thresholds(self.log_response_width_std
                           * RNG.standard_normal(size=n_levels))[1:-1]
                    for (a, n_levels) in zip(self.emf.attribute_grades.keys(),
                                             self.emf.rating_shape)}
        # --------------------------------------------------------------------
        return EmaSimGroup(self,
                           {self.id + f'_S{i}': self.subject_class(sc_prob=gen_sc_prob(),
                                                                   a_theta=gen_attr(),
                                                                   a_tau=gen_tau())
                            for i in range(n_subjects)})


# ----------------------------------------------------------------------
class EmaSimGroup:
    """Group of test subjects drawn from a given population
    """
    def __init__(self, pop, subjects):
        """
        :param pop: an EmaSimPopulation instance,
            from which subjects have been drawn at random
        :param subjects: dict with (s_id, s_sim)
            s_id = string id for the subject
            s_sim = an EmaSimSubject instance
        """
        self.pop = pop
        self.subjects = subjects


# -------------------------------------------------------------------------
class EmaSimExperiment:
    """Defines a simulated EMA data-collection experiment,
    with one or more groups of simulated subjects, with
    each group generated from an EmaSimPopulation instance.

    Method gen_dataset() generates a complete ema_data.EmaDataSet instance
    with EMA records for all subjects in all groups.

    The experimental procedure is defined by
    emf = an ema_data.EmaFrame instance, and
    """
    def __init__(self, emf, groups):  # ema_records=(3, 20)):
        """
        :param emf: EmaFrame instance, defining experimental parameters
        :param groups: dict with elements (g_id, g_sim),
            g_sim = an EmaSimGroup instance
        """
        self.emf = emf
        self.groups = groups

    def __repr__(self):
        return (f'{self.__class__.__name__}(\n\t' +
                ',\n\t'.join(f'{key}={repr(v)}'
                             for (key, v) in vars(self).items()) +
                '\n\t)')

    def gen_dataset(self, min_ema=3, max_ema=50):
        """Generate a complete EmaDataSet instance for this experiment,
        with one or more groups of subjects.
        :param min_ema: min random number of EMA records in each Stage
        :param max_ema: max random number of EMA records in each Stage
        :return: a single EmaDataSet instance
        """
        emd = {g: {s_id: s.gen_ema_records(self.emf, min_ema, max_ema)
                   for (s_id, s) in g_sim.subjects.items()}
               for (g, g_sim) in self.groups.items()}
        return EmaDataSet(self.emf, emd)


# --------------------------------------- module simulator function: **** not needed ?
# def gen_dataset(pcf,
#                 n_subjects,
#                 quality_mean,
#                 quality_std=0.,
#                 response_width_mean=1.,
#                 log_response_width_std=0.,
#                 lapse_prob_range=(0., 0.),
#                 subject_class=SubjectBradley,
#                 n_replications=3,
#                 pair_different=True):  # ******************************************
#     """Generate data from a simple simulated paired-comparison experiment
#     with ONE group of subjects, for ONE perceptual Attribute, in ONE Test Condition.
#     :param pcf: a PairedCompFrame object defining experimental format
#     :param n_subjects: scalar integer number of simulated subjects
#     :param quality_mean: 1D array-like list of population mean quality parameters
#     :param quality_std: scalar or array-like list with inter-individual st.deviations
#     :param response_width_mean: scalar mean response interval width
#     :param log_response_width_std: scalar st.deviation of log(response interval widths)
#     :param lapse_prob_range: tuple (min, max) of individual lapse probability
#     :param subject_class: class of subject model
#     :param n_replications: scalar integer with number of comparisons (A, B),
#         plus same number for (B, A)
#     :param pair_different: boolean, allow only different objects to be compared
#
#     :return: ds= single pc_data.PairedCompDataSet instance containing all simulated results
#
#     NOTE: ds.save(...) may be called to store data in one file for each subject.
#     """
#     pcf = copy.deepcopy(pcf)
#     # use local copy, so we do not modify caller's original.
#     if pcf.objects is None:
#         pcf.objects = [f'Obj{i}' for i in range(len(quality_mean))]
#     if len(pcf.objects) != len(quality_mean):
#         raise RuntimeError('Length of quality_mean must agree with number of objects')
#     if len(pcf.attributes) > 1:
#         logger.warning(f'Same population properties for attributes {pcf.attributes}')
#         # This is allowed, but makes no sense really.
#     if len(pcf.test_factors) > 0:
#         pcf.test_factors = dict()
#         logger.warning('Using only one un-named Test Condition')
#
#     ema_pop = EmaSimPopulation(objects=pcf.objects,
#                                quality_mean={a: quality_mean
#                                              for a in pcf.attributes},
#                                quality_std=quality_std,
#                                response_width_mean=response_width_mean,
#                                log_response_width_std=log_response_width_std,
#                                lapse_prob_range=lapse_prob_range,
#                                subject_class=subject_class)
#     pc_group = ema_pop.gen_subject_group(pcf, n_subjects=n_subjects)
#     pc_exp = EmaSimExperiment(pcf,
#                               n_replications=n_replications,
#                               pair_different=pair_different)
#     return pc_exp.gen_dataset(groups={'': pc_group})


# ------------------------------------- internal help function:
# def thurstone2bradley(x):
#     """transform parameters defined on Thurstone d-prime scale,
#     to equivalent parameters on the BTL model scale
#     :param: x = array or array-like list of values in d-prime units
#     :return: array with transformed values
#     """
#     return logistic.ppf(norm(scale=np.sqrt(2)).cdf(x))
#
#
# def bradley2thurstone(x):
#     """transform parameters defined on Bradley scale,
#     to equivalent parameters on the Thurstone model scale
#     :param: x = array or array-like list of values in BTL units
#     :return: array with transformed values
#     """
#     return norm.ppf(logistic.cdf(x), scale=np.sqrt(2))
