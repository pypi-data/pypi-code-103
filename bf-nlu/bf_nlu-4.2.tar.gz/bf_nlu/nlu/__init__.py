import logging

import bf_nlu
from bf_nlu.nlu.train import train
from bf_nlu.nlu.test import run_evaluation as test
from bf_nlu.nlu.test import cross_validate
from bf_nlu.nlu.training_data import load_data

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = bf_nlu.__version__
