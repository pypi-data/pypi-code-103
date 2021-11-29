"""
Python generator which implements `tail -f`-like behaviour.

Usage:
```
import tail
tailed_file = tail.TailedFile("path_to_file")
while True:
    line = tailed_file.readline()
    if not line:
        sleep(5)
"""

import os


class TailedFile(object):
    def __init__(self, fn):
        self.fn = fn
        self._obj = None
        self._ino = None
        self.seek_end()

    def readline(self):
        """ read the next line in the log file """
        self.obj
        line = self._try_readline()
        if line:
            return line
        elif self.is_rotated():
            self.reopen()
        return None

    @property
    def obj(self):
        if self._obj is None:
            try:
                self._obj = open(self.fn)
                self._ino = os.fstat(self._obj.fileno()).st_ino
            except IOError:
                return None
        return self._obj

    def is_rotated(self):
        try:
            return os.stat(self.fn).st_ino != self._ino
        except OSError:
            return True

    def reopen(self):
        if self._obj:
            self._obj.close()
        self._obj = None
        self._ino = None

    def seek_end(self):
        obj = self.obj
        if obj:
            self.obj.seek(0, 2)

    def _try_readline(self):
        if not self.obj:
            return None

        where = self.obj.tell()
        line = self.obj.readline()
        if not line:
            self.obj.seek(where)
            return None
        return line

    def __repr__(self):
        return '%r' % self.fn

    def close(self):
        if self._obj:
            self._obj.close()
