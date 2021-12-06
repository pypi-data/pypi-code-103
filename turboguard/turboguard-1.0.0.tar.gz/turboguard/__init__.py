from . import core
from .core import BlacklistedError


__version__ = '1.0.0'


class Sanitizer:
    _handle = None

    def __init__(self, blacklist=None, replace=None):
        self.blacklist = blacklist or []
        self.replacelist = replace or []

    def _import_blacklist(self):
        """Slow method!"""
        for item in self.blacklist:
            if not isinstance(item, tuple):
                start, end = item, item
            else:
                start, end = item

            core.blacklist_appenditem(self._handle, ord(start), ord(end))

    def _import_replacelist(self):
        """Slow method!"""
        for item in self.replacelist:
            replace, by = item
            core.replacelist_appenditem(self._handle, ord(replace), ord(by))

    def __call__(self, string):
        return core.sanitize(self._handle, string)

    def __enter__(self):
        blacklistsize = len(self.blacklist)
        replacelistsize = len(self.replacelist)

        self._handle = core.create(blacklistsize, replacelistsize)
        self._import_blacklist()
        self._import_replacelist()
        return self

    def __exit__(self, extype, exvalue, traceback):
        core.dispose(self._handle)
        self._handle = None
