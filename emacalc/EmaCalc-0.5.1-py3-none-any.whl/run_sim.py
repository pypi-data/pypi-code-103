"""Script to simulate an Ecological Momentary Assessment (EMA) study,
collecting the results in a ema_data.EmaDataSet object,
just as if the dataset had been gathered from data files from a real experiment.

A simulated experiment may include
one or more Groups of subjects randomly drawn from one specified Population,
each performing several simulated EMA recordings,
with each EMA record specifying
(1) a nominal SCENARIO, specified in one or more dimensions,
(2) ordinal attribute_grades of one or more perceptual ATTRIBUTE(s).


*** Usage:
Copy and edit this script and run it for any desired simulation.


*** Version history:
2021-11-16, first functional version
2021-11-21, cleaned and tested beta version
"""
import numpy as np
from pathlib import Path
import logging
import pickle

from EmaCalc.ema_simulation import EmaSimPopulation, EmaSimExperiment
# from EmaCalc.ema_simulation import SubjectThurstone, SubjectBradley

from EmaCalc.ema_data import EmaFrame, EmaDataSet
from EmaCalc.ema_model import EmaModel
from EmaCalc.ema_display import EmaDisplaySet
from EmaCalc import ema_logging


# ------------------------ Set up working directory and result logging:

work_path = Path.home() / 'Documents' / 'EMA_sim'  # or whatever...
data_path = work_path / 'data'  # or whatever
result_path = work_path / 'result'  # or whatever

ema_logging.setup(save_path=work_path,
                  log_file='run_sim_log.txt')  # to save the log file
# OR
# ema_logging.setup()  # to get only console output
model_file = 'test_ema_model.pkl'  # name of saved model file (if saved)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# --------------- Define Experimental Framework: Scenarios, Attributes, and Grades

sim_scenarios = {'Stage': ('',),  # only ONE Test Stage with empty label
                 'HA': ('A', 'B'),  # two Hearing-aid programs
                 'CoSS': [f'{i}.' for i in range(1, 8)],    # Seven CoSS categories
                 }  # nominal variables, same for all (Sub-)Populations

emf = EmaFrame(scenarios=sim_scenarios,
               stage_key='Stage',
               attribute_grades={'Speech': ['Very Hard',
                                            'Hard',
                                            'Easy',
                                            'Very Easy',
                                            'Perfect']},  # ordinal rating categories
               )

# --------------- Define Population(s) to be simulated:

pop0_scenario_prob = [[1., 2., 3., 4., 5., 6., 7.],     # with 'HA' = 'A'
                      [7., 6., 5., 4., 3, 2., 1.]]      # with 'HA' = 'B'
# pop0_scenario_prob.shape == emf.scenario_shape
#   OR == emf.scenario_shape[1:] if emf.scenario_shape[0] == 1, i.e., only one Stage

# --------- Population mean for Attribute = 'Speech'
pop0_speech_mean = 0.3 * np.array(pop0_scenario_prob)
# pop0_speech_mean[i, j] = population mean for latent sensory variable, given scenario[i, j]

ema_pop_0 = EmaSimPopulation(emf,  # ***** let emf define several groups / Sub-populations ??? ********
                             scenario_prob=pop0_scenario_prob,
                             attribute_mean={'Speech': pop0_speech_mean},
                             log_scenario_std=0.3, # inter-individual standard deviation of logprob params
                             attribute_std=0.3,  # inter-individual standard deviation of attribute locations
                             log_response_width_std=0.,  # inter-individual resp.-threshold variations
                             # subject_class=SubjectBradley,
                             id='Pop0'
                             )

logger.info(f'ema_pop_0={ema_pop_0}')

# Optionally, define other populations here,
# ema_pop_1 = EmaSimPopulation(emf, ... etc)
# with SAME EmaFrame, but different mean Attribute values

# ------------------ Generate Experiment with One Group of Subjects from each Population:
ema_exp = EmaSimExperiment(emf,
                           groups={(('Age', 'old'),): ema_pop_0.gen_group(n_subjects=20)
                                   # ('Age', 'young'): ema_pop_1.gen_group(n_subjects=15)
                                   })
# NOTE: groups keys MUST be a tuple of ONE OR MORE pairs (g_factor, g_cat)
#
logger.info(f'ema_exp= {ema_exp}')
# defines true parameters for Population(s) and all Subjects in each Group

# ------------------------- Generate EMA data for all subjecdts in all Groups:

ds = ema_exp.gen_dataset(min_ema=20,    # min n of EMA records per subject
                         max_ema=80)    # max n of EMA records per subject
# = a complete EmaDataSet instance with simulated EMA records for all subjects'

# Optionally, save all data in a set of data files, one for each subject
file_format = 'xlsx'
ds.save(data_path, allow_over_write=True, fmt=file_format,
        subject='sheet',    # subject ID stored in xlsx sheet name
        ema_vars={'Stage': 'A',
                  'HA': 'B',
                  'CoSS': 'C',
                  'Speech': 'F'}
        )
# -> one xlsx file for each subject
# logging.info(ds)
logging.info('Simulated EMA data saved in ' + str(data_path) + f' as {file_format} files')

# ------------------------------- Learn Analysis Model from simulated data set:
# -------- Test re-loading simulated data from saved xlsx files:

logging.info('Simulated EMA data loaded from ' + str(data_path) + f' as {file_format} files')
ds = EmaDataSet.load(emf, data_path,
                     grouping={'Age': ('old',),  # ('old', 'young'),
                               },
                     subject='sheet',
                     ema_vars={'HA': 'B',
                               'CoSS': 'C',
                               'Speech': 'F'}
                     )

logger.info(f'Using data ds=\n{ds}')

# Model ordinal-regression effects of Scenarios on each Attribute:
regression_effects = [  # 'HA', 'CoSS',  # only main linear regression effects, no interactions
                ('HA', 'CoSS')  # main AND interaction effects
                # 'Stage',  # if there are several Stage categories
                ]
# NOTE: including interaction effects -> many free model parameters,
#   possibly -> less precise estimation for each parameter
# In this example: ['HA', 'CoSS'] -> (2 - 1) + (7 - 1) = 7 regression-effect parameters
#                [('HA', 'CoSS')] -> 2 * 7 - 1 = 13 regression-effect parameters

emm = EmaModel.initialize(ds, regression_effects,
                          max_n_comp=10)
# max_n_comp = max number of mixture components in population model
logger.info(f'PriorComp.mean.learned_weight= {emm.base.comp_prior.mean.learned_weight}')
logger.info(f'PriorComp.prec.shape= {emm.base.comp_prior.prec.a}')

ll = emm.learn(max_hours=1.)
logger.info('ll= ' + np.array2string(np.array(ll), precision=5))
emm.prune()  # keep only active mixture components

# -------- Save learned EmaModel instance (optional):
with (work_path / model_file).open('wb') as f:
    pickle.dump(emm, f)

# ------------------------------- generate all result displays:

emd = EmaDisplaySet.display(emm,
                            scenarios=['CoSS',  # CoSS profile, aggregated across HA
                                       ('CoSS', 'HA'),  # CoSS profiles, conditional on HA
                                       ('HA', 'CoSS'),  # HA profiles, conditional on CoSS
                                       ],
                            attributes=[('Speech', 'CoSS'),     # Speech, main effect of CoSS
                                        ('Speech', 'HA'),       # Speech, main effect of HA
                                        ('Speech', ('CoSS', 'HA')),     # joint effect of both
                                        ],
                            population_individual=True,  # random individual in the population
                            population_mean=True,  # population mean
                            subjects=False,  # individual results -> MANY plots and tables
                            show_intervals=True,  # response thresholds in attribute plots
                            percentiles=[5, 25, 50, 75, 95],  # in profile plots and tables
                            credibility_limit=0.7,  # minimum credibility in difference tables
                            figure_format='pdf',  # or 'eps', 'jpg'
                            table_format='latex',  # or 'tab' for tab-limited text style
                            )

# ------------------------------- save all displays in directory tree
emd.save(result_path)

logging.info(f'All result displays saved in {result_path}')

logging.shutdown()
