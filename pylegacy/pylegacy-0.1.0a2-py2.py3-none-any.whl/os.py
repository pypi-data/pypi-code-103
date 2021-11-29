"""Legacy :mod:`os` module."""
from __future__ import absolute_import

# Add temporary imports.
import sys as __sys

# Import `os` members.
from os import *
from os import __all__
from os import __doc__
__all__ = list(__all__)

# Start with backports.
if __sys.version_info[:2] < (3, 2):

    # Backport info:
    # - Python 3.2: first appeareance.
    # pylint: disable=redefined-outer-name
    def makedirs(name, mode=0o777, exist_ok=False):
        """makedirs(name [, mode=0o777][, exist_ok=False])

        Super-mkdir; create a leaf directory and all intermediate ones.  Works like
        mkdir, except that any intermediate path segment (not just the rightmost)
        will be created if it does not exist. If the target directory already
        exists, raise an OSError if exist_ok is False. Otherwise no exception is
        raised.  This is recursive.
        """

        import os
        import errno

        exist_ok = bool(exist_ok)
        try:
            os.makedirs(name, mode)
        except OSError as err:
            if exist_ok and os.path.isdir(name) and err.errno == errno.EEXIST:
                return
            raise

    if "makedirs" not in __all__:
        __all__.append("makedirs")

if (3, 3) <= __sys.version_info[:2] < (3, 5):

    # Backport info:
    # - Python 3.3: first time that `os.environ` was removed from `__all__`.
    # - Python 3.5: `os.environ` is brought back to `__all__`.
    # pylint: disable=redefined-outer-name
    from os import environ
    __all__.append("environ")


# Remove temporary imports.
del __sys
