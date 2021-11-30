from ...data._data_provider import Data
from ._tools import _get_query_parameter


class BaseData(Data):
    def __init__(self, raw_json, dataframe=None, iter_object=None):
        super().__init__(raw_json)
        url = self.raw.get("@nextLink", None)
        self.raw["skip_token"] = _get_query_parameter("skipToken", url)
        self._dataframe = dataframe
        self._iter_object = iter_object


class BucketData(BaseData):
    @property
    def buckets(self):
        return self._iter_object


class FileSetData(BaseData):
    @property
    def file_sets(self):
        return self._iter_object


class PackageData(BaseData):
    @property
    def packages(self):
        return self._iter_object


class FileData(BaseData):
    @property
    def files(self):
        return self._iter_object
