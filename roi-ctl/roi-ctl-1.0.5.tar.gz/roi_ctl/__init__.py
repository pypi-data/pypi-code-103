import importlib
import os
import sys

from .roi_ctl import *

# MODULE REGISTER
globals().update(importlib.import_module('roi_ctl').__dict__)

# STATIC PATH
if sys.platform.startswith('linux'):
	os.environ['ROI_CTL_STATIC'] = os.path.dirname(os.path.abspath(__file__))