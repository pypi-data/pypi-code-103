from .stream_connection_configuration import StreamConnectionConfiguration
from .. import StreamServiceInformation
from ..null_session import NullSession


class NullStreamConnectionConfiguration(StreamConnectionConfiguration):
    def __init__(self):
        StreamConnectionConfiguration.__init__(self, NullSession(), [], [])

    def _build_stream_connection_url(self, stream_service_information):
        return ""

    @property
    def stream_service_information(self):
        return StreamServiceInformation("", "", "", "", "", "")
