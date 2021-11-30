# pyant

ant_root_path = os.path.dirname(os.path.abspath(__file__))
if ant_root_path not in sys.path:
    sys.path.append(ant_root_path)

__version__ = '0.4.1'

from pyant import *
from .rpc_call_helper import call, async_call, call_mf
from .logger import log_dbg, log_inf, log_wrn, log_err, log_fat
