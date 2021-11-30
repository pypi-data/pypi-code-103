# coding: utf-8


import abc
from typing import TYPE_CHECKING

from ..proxy_info import ProxyInfo

if TYPE_CHECKING:
    from .. import Session


class StreamConnectionConfiguration(abc.ABC):
    """this class is designed for storing the stream connection configuration.
    i.e. desktop data api proxy, service discovery, realtime-distribution-system, etc.
    """

    #   default delay time before do a reconnection in secs
    _DefaultReconnectionDelayTime_secs = 5

    def __init__(
        self,
        session: "Session",
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        self._session = session

        self._stream_service_information_list = stream_service_information_list

        self._supported_protocol_list = supported_protocol_list

        # 	store the current index of stream service
        self._current_stream_service_information_index = 0

    @property
    def stream_service_information(self):
        return self._stream_service_information_list[
            self._current_stream_service_information_index
        ]

    @property
    def url(self):
        return self._build_stream_connection_url(self.stream_service_information)

    @property
    def url_scheme(self):
        return self.stream_service_information.scheme

    @property
    def urls(self):
        return [
            self._build_stream_connection_url(stream_service_information)
            for stream_service_information in self._stream_service_information_list
        ]

    @property
    def headers(self):
        return []

    @property
    def data_formats(self):
        return self.stream_service_information.data_formats

    @property
    def supported_protocols(self):
        return self._supported_protocol_list

    @property
    def reconnection_delay_secs(self):
        return (
            self._current_stream_service_information_index
            * self._DefaultReconnectionDelayTime_secs
        )

    def set_next_available_websocket_url(self):
        self._current_stream_service_information_index = (
            self._current_stream_service_information_index + 1
            if self._current_stream_service_information_index + 1
            < len(self._stream_service_information_list)
            else 0
        )

    def reset_reconnection_config(self):
        self._current_stream_service_information_index = 0

    @property
    def no_proxy(self):
        return ProxyInfo.get_no_proxy()

    @property
    def proxy_config(self):
        proxies_info = ProxyInfo.get_proxies_info()
        if self.url_scheme == "wss":
            # try to get https proxy then http proxy if https not configured
            return proxies_info.get("https", proxies_info.get("http", None))
        else:
            return proxies_info.get("http", None)

    @property
    def data_fmt(self):
        if not self.data_formats:
            return ""
        return self.data_formats[0]

    @property
    def delay(self):
        return self.reconnection_delay_secs

    def set_next_url(self):
        self.set_next_available_websocket_url()

    def set_next_delay(self, val=None):
        self.reset_reconnection_config()

    @abc.abstractmethod
    def _build_stream_connection_url(self, stream_service_information):
        pass

    def __str__(self) -> str:
        s = (
            f"{self.__class__.__name__}={{\n"
            f"\t\tstream_service_information={self.stream_service_information},\n"
            f"\t\turl={self.url},\n"
            f"\t\turl_scheme={self.url_scheme},\n"
            f"\t\turls={self.urls},\n"
            f"\t\theaders={self.headers}, "
            f"data_formats={self.data_formats}, "
            f"supported_protocols={self.supported_protocols}, "
            f"reconnection_delay_secs={self.reconnection_delay_secs}, "
            f"no_proxy={self.no_proxy}, "
            f"proxy_config={self.proxy_config}, "
            f"data_fmt={self.data_fmt}, "
            f"delay={self.delay}}}"
        )
        return s


class DesktopStreamConnectionConfiguration(StreamConnectionConfiguration):
    def __init__(
        self,
        session: object,
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        StreamConnectionConfiguration.__init__(
            self, session, stream_service_information_list, supported_protocol_list
        )

    @property
    def headers(self):
        if self._session._access_token:
            return [f"x-tr-applicationid: {self._session.app_key}",
                    f"Authorization: Bearer {self._session._access_token}"]
        else:
            return [f"x-tr-applicationid: {self._session.app_key}"]


    def _build_stream_connection_url(self, stream_service_information):
        return f"{stream_service_information.scheme}://{stream_service_information.host}:{stream_service_information.port}/{stream_service_information.path}"


class RealtimeDistributionSystemConnectionConfiguration(StreamConnectionConfiguration):
    def __init__(
        self,
        session: object,
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        StreamConnectionConfiguration.__init__(
            self, session, stream_service_information_list, supported_protocol_list
        )

    def _build_stream_connection_url(self, stream_service_information):
        path = (
            "WebSocket"
            if stream_service_information.path is None
            or stream_service_information.path == ""
            else f"{stream_service_information.path}"
        )
        return f"{stream_service_information.scheme}://{stream_service_information.host}:{stream_service_information.port}/{path}"
