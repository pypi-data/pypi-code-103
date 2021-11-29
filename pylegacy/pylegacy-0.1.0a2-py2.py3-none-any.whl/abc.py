"""Legacy :mod:`abc` module."""
from __future__ import absolute_import

# Add temporary imports.
import sys as __sys

# Import `abc` members.
from abc import *
from abc import __doc__
__all__ = sorted(__k for __k in globals().keys()
                 if not (__k.startswith("__") or __k.endswith("__")))

# Start with backports.
if __sys.version_info[:2] < (3, 4):

    from abc import ABCMeta

    # Backport info:
    # - Python 3.4: first appeareance.
    ABC = ABCMeta(str("ABC"), (), {
        "__doc__": "\n".join([
            "Helper class that provides a standard way to create an ABC using",
            "inheritance."]),
    })

    if "ABC" not in __all__:
        __all__.append("ABC")

# Remove temporary imports.
del __sys
