from ..delivery.data import _data_provider
from ..delivery.data._data_provider import emit_event


# ---------------------------------------------------------------------------
#   Content data
# ---------------------------------------------------------------------------


class Data(_data_provider.Data):
    pass


# ---------------------------------------------------------------------------
#   Response object
# ---------------------------------------------------------------------------


class Response(_data_provider.Response):
    pass


# ---------------------------------------------------------------------------
#   Response factory
# ---------------------------------------------------------------------------


class ResponseFactory(_data_provider.ResponseFactory):
    pass


# ---------------------------------------------------------------------------
#   Request factory
# ---------------------------------------------------------------------------


class RequestFactory(_data_provider.RequestFactory):
    pass


# ---------------------------------------------------------------------------
#   Connection object
# ---------------------------------------------------------------------------


class HttpSessionConnection(_data_provider.HttpSessionConnection):
    pass


# ---------------------------------------------------------------------------
#   Raw data parser
# ---------------------------------------------------------------------------


class Parser(_data_provider.Parser):
    pass


# ---------------------------------------------------------------------------
#   Content data validator
# ---------------------------------------------------------------------------


class ContentValidator(_data_provider.ContentValidator):
    pass


# ---------------------------------------------------------------------------
#   Data provider
# ---------------------------------------------------------------------------


class DataProvider(_data_provider.DataProvider):
    pass


# ---------------------------------------------------------------------------
#   Provider layer
# ---------------------------------------------------------------------------


class ContentProviderLayer(_data_provider.DataProviderLayer):
    def __init__(self, content_type, **kwargs):
        _data_provider.DataProviderLayer.__init__(
            self,
            data_type=content_type,
            **kwargs,
        )
