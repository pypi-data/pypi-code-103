import logging

from bf_nlu import version

# define the version before the other imports since these need it
__version__ = version.__version__

from bf_nlu.run import run
from bf_nlu.train import train
from bf_nlu.test import test

logging.getLogger(__name__).addHandler(logging.NullHandler())
