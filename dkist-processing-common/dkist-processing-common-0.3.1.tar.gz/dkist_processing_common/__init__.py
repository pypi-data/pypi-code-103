from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

from .tasks import *

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"
