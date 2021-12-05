import abc
import collections

class ListResult:
    def __init__(self, ok):
        self.results = []
        self.ok = ok

    @abc.abstractmethod
    def add_result(self, **kwargs):
        pass

    def get_results(self):
        return self.results

class PackageListResult(ListResult):
    PackageResult = collections.namedtuple(
        'PackageResult', ['name', 'link']
    )

    def add_result(self, **kwargs):
        self.results.append(self.PackageResult(**kwargs))

class PackageFileListResult(ListResult):
    PackageFileResult = collections.namedtuple(
        'PackageFileResult', ['name', 'link', 'requires_python']
    )

    def add_result(self, **kwargs):
        self.results.append(self.PackageFileResult(**kwargs))

class ABCRepository(abc.ABC):
    def __init__(
            self, *, exclude_packages = None, include_packages = None,
            include_package_files = None, exclude_package_files = None,
            stop_on_package_match = True
    ):
        def coalesce(val, default):
            if val is not None:
                return val
            else:
                return default

        self.stop_on_package_match = stop_on_package_match
        self.exclude_packages = coalesce(exclude_packages, [])
        self.include_packages = coalesce(include_packages, [])
        self.exclude_package_files = coalesce(exclude_package_files, [])
        self.include_package_files = coalesce(include_package_files, [])

    @staticmethod
    def matches_includes(name, patterns):
        return all(fnmatch.fnmatchcase(name, pat) for pat in patterns)

    @staticmethod
    def matches_excludes(name, patterns):
        return not any(fnmatch.fnmatchcase(name, pat) for pat in patterns)

    @abc.abstractmethod
    def list_all_packages(self):
        pass

    def list_packages(self):
        all_results = self.list_all_packages()
        ret = PackageListResult(all_results.ok)
        if not ret.ok:
            return ret
        else:
            for result in all_results.results:
                if self.matches_includes(result.name, self.include_packages):
                    if self.matches_excludes(result.name, self.exclude_packages):
                        ret.add_result(name = result.name, link = result.link)
        return ret

    def list_package_files(self, package_name):
        all_results = self.list_all_package_files(package_name)
        ret = PackageFileListResult(all_results.ok)
        if not ret.ok:
            return ret
        else:
            for result in all_results.results:
                if self.matches_includes(result.name, self.include_package_files):
                    if self.matches_excludes(result.name, self.exclude_package_files):
                        ret.add_result(name = result.name, link = result.link, requires_python = result.requires_python)
        return ret
        

    @abc.abstractmethod
    def list_all_package_files(self, package_name):
        pass

    @abc.abstractmethod
    def get_package_file(self, package_name, file_name):
        pass
