"""
Fanta
~~~~~
Pythonic API Wrapper For Discord

:copyright: 2021 RPSMain & 2021 Tag-Epic
:license: MIT
"""

__title__ = "fanta"
__author__ = "RPSMain"
__license__ = "MIT"
__copyright__ = "Copyright 2021 RPSMain"
__version__ = "0.1.0"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal
from .client import *
from .dispatcher import *
from .exceptions import *
from .http import *
from .ratelimiter import *
from .shard import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(
    major=0, minor=1, micro=0, releaselevel="alpha", serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
