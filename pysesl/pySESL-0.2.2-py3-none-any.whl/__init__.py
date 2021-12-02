# flake8: noqa
# type: ignore

import pkg_resources

from .historical import calc_sl, calc_T0, calc_temp, resize_T
from .io import load_data_SESL, load_param_file
from .project import bias_correct_temps_and_resample_ics, get_ics, project_sesl

__version__ = pkg_resources.get_distribution("rhg_compute_tools").version
