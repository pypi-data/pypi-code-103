"""Legacy :mod:`builtins` module."""
from __future__ import absolute_import

# Add temporary imports.
import sys as __sys

# Import `builtins` members.
try:
    from builtins import *
    from builtins import __doc__
except ImportError:
    from __builtin__ import *
    from __builtin__ import __doc__
__all__ = sorted(__k for __k in globals().keys()
                 if not (__k.startswith("__") or __k.endswith("__")))

# Start with backports.
if __sys.version_info[:2] < (3, 2):

    # Backport info:
    # - Python 3.2: first appeareance.
    class ResourceWarning(Warning):
        """Base class for warnings about resource usage."""

    if "ResourceWarning" not in __all__:
        __all__.append("ResourceWarning")

# Remove temporary imports.
del __sys
