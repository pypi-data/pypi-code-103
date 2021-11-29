import logging

import bf_nlu

from bf_nlu.core.train import train
from bf_nlu.core.test import test
from bf_nlu.core.visualize import visualize

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = bf_nlu.__version__
