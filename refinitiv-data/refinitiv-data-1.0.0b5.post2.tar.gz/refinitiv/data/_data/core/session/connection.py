import abc
import logging
import sys
import urllib.parse
from typing import TYPE_CHECKING, Optional

import validators

from ._session import Session
from .authentication_token_handler_thread import AuthenticationTokenHandlerThread
from .stream_service_discovery.stream_connection_configuration import (
    RealtimeDistributionSystemConnectionConfiguration,
    DesktopStreamConnectionConfiguration,
)
from .stream_service_discovery.stream_service_discovery_handler import (
    StreamServiceInformation,
    PlatformStreamServiceDiscoveryHandler,
    DesktopStreamServiceDiscoveryHandler,
)
from ... import configure

from ...errors import PlatformSessionError
from ...tools import urljoin

if TYPE_CHECKING:
    from ...configure import _RDPConfig


def get_discovery_endpoint_url(
    config: "_RDPConfig", config_name: str, config_endpoint_name: str, root_url: str
) -> str:
    base_path = config.get_str(f"{config_name}.url")
    endpoint_path = config.get_str(f"{config_endpoint_name}.path")

    url = None
    base_path = base_path.strip()
    if base_path.startswith("/"):
        url = urljoin(root_url, base_path)

    elif validators.url(base_path):
        url = base_path

    url = urljoin(url, endpoint_path)
    return url


class SessionConnection(abc.ABC):
    def __init__(self, session):
        self._session = session

        self.log = session.log
        self.debug = session.debug

    @abc.abstractmethod
    async def get_stream_connection_configuration(self, stream_connection_name: str):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        pass

    @abc.abstractmethod
    def get_omm_login_message_key_data(self):
        pass

    @abc.abstractmethod
    async def waiting_for_stream_ready(self, open_state):
        pass

    @abc.abstractmethod
    def authorize(self):
        pass


class PlatformConnection(SessionConnection, abc.ABC):
    def __init__(self, session):
        super().__init__(session)
        self.streaming_connection_name_and_connection_type_to_status = {}

    def get_stream_status(self, streaming_connection_name):
        return self.streaming_connection_name_and_connection_type_to_status.get(
            streaming_connection_name, Session.EventCode.StreamDisconnected
        )

    def set_stream_status(self, streaming_connection_name, stream_status):
        self.streaming_connection_name_and_connection_type_to_status[
            streaming_connection_name
        ] = stream_status


class RefinitivDataConnection(PlatformConnection):
    def __init__(self, session):
        super().__init__(session)
        self._auth_thread: Optional[AuthenticationTokenHandlerThread] = None

    def get_omm_login_message_key_data(self) -> dict:
        return {
            "NameType": "AuthnToken",
            "Elements": {
                "AuthenticationToken": self._session._access_token,
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await self._session._http_request_async(
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )

    async def get_stream_connection_configuration(self, api: str):
        config = self._session.config
        root_url = self._session._get_rdp_url_root()

        _, streaming_name, endpoint_name = api.split("/")
        config_name = f"apis.streaming.{streaming_name}"
        config_endpoint_name = f"{config_name}.endpoints.{endpoint_name}"

        endpoint_websocket_url = config.get(f"{config_endpoint_name}.websocket-url")
        discovery_endpoint_url = get_discovery_endpoint_url(
            config, config_name, config_endpoint_name, root_url
        )
        protocols = config.get_list(f"{config_endpoint_name}.protocols")

        self._session.debug(f"          {api} supported protocol are {protocols}")

        if endpoint_websocket_url is not None:
            self._session.debug(
                f"override streaming by WebSocket endpoint url : {endpoint_websocket_url}"
            )

            websocket_url_parse = urllib.parse.urlparse(endpoint_websocket_url)
            stream_service_information = StreamServiceInformation(
                scheme=websocket_url_parse.scheme,
                host=websocket_url_parse.hostname,
                port=websocket_url_parse.port,
                path=websocket_url_parse.path.lstrip("/"),
                data_formats=["unknown"],
                location=None,
            )

            return RealtimeDistributionSystemConnectionConfiguration(
                self._session, [stream_service_information], protocols
            )

        elif discovery_endpoint_url is not None:
            self.debug(f"using discovery endpoint url : {discovery_endpoint_url}")
            streaming, streaming_name, endpoint_name = api.split("/")
            assert streaming == "streaming"

            streaming_connection_endpoint_location_name = (
                f"apis.streaming.{streaming_name}.endpoints.{endpoint_name}.locations"
            )
            try:
                prefer_stream_service_locations = configure.get_list(
                    streaming_connection_endpoint_location_name
                )
            except KeyError:
                prefer_stream_service_locations = []

            service_discovery_handler = PlatformStreamServiceDiscoveryHandler(
                self._session,
                discovery_endpoint_url,
                prefer_stream_service_locations=prefer_stream_service_locations,
            )
            stream_service_information = (
                await service_discovery_handler.get_stream_service_information()
            )

            return RealtimeDistributionSystemConnectionConfiguration(
                self._session,
                stream_service_information,
                protocols,
            )

        else:
            raise ValueError(
                "ERROR!!! streaming connection needed by specific url and path in endpoint section or specific WebSocket url."
            )

    async def waiting_for_stream_ready(self, open_state):
        pass

    def _initialize_auth_thread(self):
        self._auth_thread = AuthenticationTokenHandlerThread(
            self._session,
            self._session._grant,
            self._session.authentication_token_endpoint_url,
            server_mode=self._session.server_mode,
        )

    def open(self):
        self._initialize_auth_thread()
        self.authorize()

    def authorize(self):
        while True:
            is_authorize_failed = False

            try:
                self._auth_thread.authorize()
            except Exception:
                if not self._session.server_mode:
                    self._session.error(
                        f"ERROR!!! failed to request an authorization to platform.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(auto-reconnection is disabled)"
                    )

                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{sys.exc_info()[0]}.",
                    )

                else:
                    self._session.warning(
                        "WARNING!!! retrying after failed to request an authorization to platform.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(auto-reconnection is enabled)"
                    )
                    is_authorize_failed = True

            self._session.debug(
                f"               waiting for authorize is ready.........."
            )
            self._auth_thread.wait_for_authorize_ready()
            if is_authorize_failed or self._auth_thread.is_error():
                if not self._session.server_mode:
                    self._session.error(
                        "ERROR!!! CANNOT authorize to RDP authentication endpoint.\n"
                        f"Unexpected error {self._auth_thread.last_exception}.\n"
                        "(auto-reconnection is disabled)"
                    )

                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{self._auth_thread.last_exception}",
                    )

                else:
                    self._session.warning(
                        "WARNING!!! retrying after authentication token thread failed.\n"
                        f"Unexpected error {self._auth_thread.last_exception}."
                    )

                    try:
                        self._auth_thread.stop()
                    except Exception:
                        self._session.warning(
                            "WARNING!!! CANNOT properly stop authentication token handler thread .\n"
                            f"Unexpected error {sys.exc_info()[0]}."
                        )

                    self._initialize_auth_thread()

            else:
                self._session.debug(
                    "Successfully request an authorization by authentication token handler thread."
                )
                break

    def close(self):
        self.debug("Close platform session...")
        self._auth_thread and self._auth_thread.stop()
        return super().close()


class DeployedConnection(PlatformConnection):
    def __init__(self, session):
        super().__init__(session)
        self.streaming_connection_name_and_connection_type_to_status[
            self._session._deployed_platform_connection_name
        ] = Session.EventCode.StreamDisconnected

    def get_omm_login_message_key_data(self):
        return {
            "Name": self._session._dacs_params.deployed_platform_username,
            "Elements": {
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        raise PlatformSessionError(
            -1,
            "Error!!! Platform session cannot connect to refinitiv dataplatform. "
            "Please check or provide the access right.",
        )

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        if self._session._deployed_platform_host is None:
            realtime_distribution_system_url_key = f"{configure.keys.platform_realtime_distribution_system(self._session.name)}.url"
            realtime_distribution_system_url = configure.get_str(
                realtime_distribution_system_url_key
            )
            self._session.debug(
                f"using the Refinitiv realtime url at {realtime_distribution_system_url}"
            )

            realtime_distribution_system_url_parse = urllib.parse.urlparse(
                realtime_distribution_system_url
            )
            self._session.debug(
                f"      realtime_distribution_system scheme   = {realtime_distribution_system_url_parse.scheme}"
            )
            self._session.debug(
                f"      realtime_distribution_system endpoint = {realtime_distribution_system_url_parse.hostname}"
            )
            self._session.debug(
                f"      realtime_distribution_system port     = {realtime_distribution_system_url_parse.port}"
            )

            stream_service_information = StreamServiceInformation(
                scheme=realtime_distribution_system_url_parse.scheme,
                host=realtime_distribution_system_url_parse.hostname,
                port=realtime_distribution_system_url_parse.port,
                path=None,
                data_formats=["tr_json2"],
                location=None,
            )
        else:
            (
                deployed_platform_hostname,
                deployed_platform_port,
            ) = self._session._deployed_platform_host.split(":")

            stream_service_information = StreamServiceInformation(
                scheme="ws",
                host=deployed_platform_hostname,
                port=deployed_platform_port,
                path=None,
                data_formats=["tr_json2"],
                location=None,
            )

        return RealtimeDistributionSystemConnectionConfiguration(
            self._session,
            [
                stream_service_information,
            ],
            [
                "OMM",
            ],
        )

    async def waiting_for_stream_ready(self, open_state):
        open_state()

    def open(self):
        super().open()

    def authorize(self):
        pass

    def close(self):
        self.log(logging.DEBUG, "Close platform session...")
        super().close()


class RefinitivDataAndDeployedConnection(DeployedConnection, RefinitivDataConnection):
    def __init__(self, session):
        DeployedConnection.__init__(self, session)
        RefinitivDataConnection.__init__(self, session)

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await RefinitivDataConnection.http_request_async(
            self,
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        if stream_connection_name.startswith("streaming/pricing/main"):
            return await DeployedConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )
        else:
            return await RefinitivDataConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )

    def open(self):
        RefinitivDataConnection.open(self)

    def authorize(self):
        RefinitivDataConnection.authorize(self)

    def close(self):
        RefinitivDataConnection.close(self)


class DesktopConnection(SessionConnection):
    def open(self):
        # do nothing
        pass

    def close(self):
        # do nothing
        pass

    def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        # do nothing
        pass

    def get_omm_login_message_key_data(self):
        # do nothing
        pass

    async def waiting_for_stream_ready(self, open_state):
        # do nothing
        pass

    def authorize(self):
        # do nothing
        pass

    async def get_stream_connection_configuration(self, api: str):
        config = self._session.config
        root_url = self._session._get_rdp_url_root()

        _, streaming_name, endpoint_name = api.split("/")
        config_name = f"apis.streaming.{streaming_name}"
        config_endpoint_name = f"{config_name}.endpoints.{endpoint_name}"

        endpoint_websocket_url = config.get(f"{config_endpoint_name}.websocket-url")
        discovery_endpoint_url = get_discovery_endpoint_url(
            config, config_name, config_endpoint_name, root_url
        )
        protocols = config.get_list(f"{config_endpoint_name}.protocols")

        self._session.debug(f"          {api} supported protocol are {protocols}")

        if endpoint_websocket_url is not None:

            self._session.debug(
                f"\nOverride streaming by WebSocket endpoint url : "
                f"{endpoint_websocket_url}\n"
            )

            websocket = urllib.parse.urlparse(endpoint_websocket_url)

            base_session_url = urllib.parse.urlparse(self._session._base_url)

            if websocket.netloc != base_session_url.netloc:
                raise ValueError(
                    f"Missmatch between websocket url and base session url\n"
                    f"{websocket.netloc} != {base_session_url.netloc}"
                )

            stream_service_information = [
                StreamServiceInformation(
                    scheme=websocket.scheme,
                    host=websocket.hostname,
                    port=websocket.port,
                    path=websocket.path.lstrip("/"),
                    data_formats=["unknown"],
                    location=None,
                )
            ]

        elif discovery_endpoint_url is not None:

            service_discovery_handler = DesktopStreamServiceDiscoveryHandler(
                self._session, discovery_endpoint_url
            )
            stream_service_information = (
                await service_discovery_handler.get_stream_service_information()
            )
        else:
            raise ValueError(
                "ERROR!!! streaming connection needed by specific url"
                " and path in endpoint section or specific WebSocket url."
            )

        stream_connection_configuration = DesktopStreamConnectionConfiguration(
            self._session,
            stream_service_information,
            protocols,
        )

        return stream_connection_configuration
