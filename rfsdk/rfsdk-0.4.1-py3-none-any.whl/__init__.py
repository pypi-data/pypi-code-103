# rfsdk
import os
import sys

_rfsdk_root_path = os.path.dirname(os.path.abspath(__file__))
if _rfsdk_root_path not in sys.path:
    sys.path.append(_rfsdk_root_path)

__version__ = '0.4.0'
