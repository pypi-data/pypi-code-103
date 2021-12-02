import logging

from . import notebook
from .client import Session
from .version import __version__

logging.getLogger("curvenote").addHandler(logging.NullHandler())
