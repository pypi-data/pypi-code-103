"""Init module for the library."""
import os
from ._version import get_versions
from .LocalClassifierPerNode import LocalClassifierPerNode
from .LocalClassifierPerParent import LocalClassifierPerParent
from .LocalClassifierPerLevel import LocalClassifierPerLevel

__version__ = get_versions()["version"]
del get_versions

__all__ = [
    "LocalClassifierPerNode",
    "LocalClassifierPerParent",
    "LocalClassifierPerLevel",
]
