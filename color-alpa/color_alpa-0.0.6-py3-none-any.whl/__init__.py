# flake8: noqa
import pkg_resources

__version__ = pkg_resources.get_distribution("color-alpa").version

from .color import Color
from .color import Colour