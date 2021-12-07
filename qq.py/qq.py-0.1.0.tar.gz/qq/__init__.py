__title__ = 'qq'
__author__ = 'Foxwhite'
__license__ = 'MIT'
__version__ = '0.1.0'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging

from .client import *
from .guild import *

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
