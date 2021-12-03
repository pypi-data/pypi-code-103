
from generallibrary import deco_cache, initBases
from generalfile.optional_dependencies._extension import _Extension

import dill


class Path_Pickle:
    """ Pickle methods for Path. """
    @property
    @deco_cache()
    def pickle(self):
        """ Easily write and read python objects with pickle. """
        return _Pickle(self)


@initBases
class _Pickle(_Extension):
    def write(self, obj=None, overwrite=False):
        """ Write to this path with a given object. """
        with self.WriteContext(self.path, overwrite=overwrite) as write_path:
            return write_path.open_operation("wb", lambda stream: dill.dump(obj=obj, file=stream), encoding=None)

    def read(self, default=...):
        """ Read from this path to get an object. """
        with self.ReadContext(self.path) as read_path:
            return read_path.open_operation("rb", lambda stream: dill.load(file=stream), encoding=None, no_file_default=default)









































