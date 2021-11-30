# coding: utf-8

from pandas import DataFrame

from .._content_provider import DataProvider, RequestFactory, ResponseFactory
from ...delivery.data.endpoint import EndpointData

# ---------------------------------------------------------------------------
#   Content data
# ---------------------------------------------------------------------------

_response_universe_name = "universe"
_response_ric_name = "ric"
_response_display_name_name = "displayName"
_response_service_name_name = "serviceName"
_response_data_name = "data"
_response_constituents_name = "constituents"


def _convert_raw_to_dataframe(raw):
    universe = raw[_response_universe_name]
    ric = universe[_response_ric_name]
    data = raw[_response_data_name]
    constituents = data[_response_constituents_name]
    _df = None
    if len(constituents):
        _df = DataFrame({ric: constituents})
    else:
        _df = DataFrame([], columns=[ric])
    if not _df.empty:
        _df = _df.convert_dtypes()
    return _df


class Data(EndpointData):
    @property
    def df(self):
        if self._dataframe is None and self._raw:
            self._dataframe = _convert_raw_to_dataframe(self._raw)
        return self._dataframe


# ---------------------------------------------------------------------------
#   Request factory
# ---------------------------------------------------------------------------


class ChainsRequestFactory(RequestFactory):
    def get_url(self, *args, **kwargs):
        url = args[1]
        url = url + "?universe={universe}"
        return url

    def get_path_parameters(self, *_, **kwargs):
        universe = kwargs.get("universe")
        if universe is None:
            return {}
        return {"universe": universe}


# ---------------------------------------------------------------------------
#   Data provider
# ---------------------------------------------------------------------------

chains_data_provider = DataProvider(
    request=ChainsRequestFactory(),
    response=ResponseFactory(data_class=Data),
)
