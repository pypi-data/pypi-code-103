
from generallibrary import Date
from generalfile import Path

from requests import ConnectionError


class _PackagerPypi:
    def get_latest_release(self):
        """ Use current datetime if bumped, otherwise fetch.

            :param generalpackager.Packager self: """
        try:
            bumped = self.is_bumped()
        except ConnectionError:
            return "Failed fetching"

        if bumped:
            return Date.now()
        else:
            return self.pypi.get_date()

    def reserve_name(self):
        """ Reserve a name on PyPI with template files.
            Untested.

            :param generalpackager.Packager self: """
        path = Path.get_cache_dir() / "python/pypi_reserve"  # type: Path
        packager = type(self)(self.name, path=path)
        packager.create_blank_locally(install=False)
        packager.localrepo.upload()
        path.delete()




























