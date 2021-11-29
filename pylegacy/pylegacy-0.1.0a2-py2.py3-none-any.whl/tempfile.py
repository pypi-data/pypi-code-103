"""Legacy :mod:`tempfile` module."""
from __future__ import absolute_import

# Add temporary imports.
import sys as __sys

# Import `tempfile` members.
from tempfile import *
from tempfile import __all__
from tempfile import __doc__
__all__ = list(__all__)

# Start with backports.
if __sys.version_info[:2] < (3, 4):

    import shutil as _shutil
    import warnings as _warnings
    from tempfile import template
    from tempfile import mkdtemp
    from . import weakref as _weakref

    # Backport info:
    # - Python 3.2: first appeareance.
    # - Python 3.4: stable implementation before signature update.
    # pylint: disable=missing-docstring
    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        def __init__(self, suffix="", prefix=template, dir=None):
            self.name = mkdtemp(suffix, prefix, dir)
            self._finalizer = _weakref.finalize(
                self, self._cleanup, self.name,
                warn_message="Implicitly cleaning up {0!r}".format(self))

        @classmethod
        def _cleanup(cls, name, warn_message):
            from . builtins import ResourceWarning
            _shutil.rmtree(name)
            _warnings.warn(warn_message, ResourceWarning)

        def __repr__(self):
            return "<{0} {1!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def cleanup(self):
            if self._finalizer.detach():
                _shutil.rmtree(self.name)

    if "TemporaryDirectory" not in __all__:
        __all__.append("TemporaryDirectory")

# Remove temporary imports.
del __sys
