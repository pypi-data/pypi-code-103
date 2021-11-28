import os as _os


class DiskCacheable(object):
    """Mixin class which provides disk caching functionality to the derived
    classes.

    The derived class must define an encode and decode method which is called
    while writing the data to or from disk.
    """

    def to_disk(self, path, *args, **kwargs):
        """Serializes the object instance to specified path on disk.
        """
        dname = _os.path.dirname(path)
        if not _os.path.lexists(dname):
            _os.makedirs(dname)
        with open(path, "w") as f:
            # check if the encode method for the class is defined. If not, lets
            #  search for the encode method in any of the parent classes using super
            if hasattr(self, "encode"):
                f.write(self.encode(*args, **kwargs))
            else:
                f.write(super().encode(*args, **kwargs))
        return

    @classmethod
    def from_disk(cls, path):
        """Deserialize an object instance from specified file on disk.
        """
        if _os.path.isfile(path):
            with open(path, "r") as f:
                return cls.decode(f.read())
        raise IOError("file not found.: {0}".format(path))
