"""
DEPRECATED: use the `.sequencing.automation` module instead.

Module for managing automation sequences (series of Steps).
"""
import warnings
from .sequencing.automation import Automation, build_automation_sequence

warnings.warn(  # v6
    'the automation module has been moved into the sequencing subpackage, please update your imports',
    DeprecationWarning,
    stacklevel=2,
)
