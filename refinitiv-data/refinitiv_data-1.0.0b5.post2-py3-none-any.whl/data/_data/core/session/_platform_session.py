# coding: utf-8

__all__ = ["PlatformSession"]

import urllib.parse

from ._session import Session
from ._session_cxn_type import SessionCxnType
from ._session_type import SessionType
from .grant_password import GrantPassword
from ...open_state import OpenState
from ...tools import create_repr, urljoin


class PlatformSession(Session):
    """
    This class is designed for handling the session to Refinitiv Data Platform (RDP)
    or Deployed Platform (TREP)
    - Refinitiv Data Platform are including handling an authentication and
        a token management (including refreshing token),
        also handling a real-time service discovery to get
        the service websocket endpoint and initialize the login for streaming
    - Deployed Platform is including the login for streaming
    """

    type = SessionType.PLATFORM

    def __init__(
        self,
        app_key=None,
        grant=None,
        signon_control=None,
        deployed_platform_host=None,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        on_state=None,
        on_event=None,
        name="default",
        auto_reconnect=None,
        server_mode=None,
        base_url=None,
        auth_url=None,
        auth_authorize=None,
        auth_token=None,
        realtime_distribution_system_url=None,
    ):
        super().__init__(
            app_key,
            on_state=on_state,
            on_event=on_event,
            deployed_platform_username=deployed_platform_username,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            name=name,
        )

        if grant and isinstance(grant, GrantPassword):
            self._grant = grant

        self._take_signon_control = signon_control if signon_control else True

        self._auto_reconnect = auto_reconnect
        self._server_mode = server_mode
        self._base_url = base_url
        self._auth_url = auth_url
        self._auth_authorize = auth_authorize
        self._auth_token = auth_token
        self._realtime_dist_system_url = realtime_distribution_system_url

        self._access_token = None

        self._deployed_platform_host = deployed_platform_host
        self._deployed_platform_connection_name = self.name

        if self._deployed_platform_host is None and self._realtime_dist_system_url:
            parse_result = urllib.parse.urlparse(self._realtime_dist_system_url)
            self._deployed_platform_host = parse_result.netloc
            self.debug(
                f"Using the Refinitiv realtime distribution system : "
                f"url at {self._realtime_dist_system_url},\n"
                f"deployed_platform_host={self._deployed_platform_host}"
            )

        elif self._deployed_platform_host and not self._realtime_dist_system_url:
            self.debug(
                f"Using the specific "
                f"deployed_platform_host={self._deployed_platform_host}"
            )

        elif self._deployed_platform_host and self._realtime_dist_system_url:
            # what to do ?
            pass

        self._logger.debug(
            f"PlatformSession created with following parameters:"
            f' app_key="{app_key}", name="{name}"'
        )

    @property
    def stream_auto_reconnection(self):
        return self._auto_reconnect

    @property
    def server_mode(self):
        return self._server_mode

    @property
    def authentication_token_endpoint_url(self) -> str:
        url = urljoin(self._get_rdp_url_root(), self._auth_url, self._auth_token)
        return url

    def _get_session_cxn_type(self) -> SessionCxnType:
        if self._grant.is_valid() and self._deployed_platform_host:
            cxn_type = SessionCxnType.REFINITIV_DATA_AND_DEPLOYED

        elif self._grant.is_valid():
            cxn_type = SessionCxnType.REFINITIV_DATA

        elif self._deployed_platform_host:
            cxn_type = SessionCxnType.DEPLOYED

        else:
            raise AttributeError(f"Can't get a session connection type")

        return cxn_type

    def _get_rdp_url_root(self):
        return self._base_url

    def _get_auth_token_uri(self):
        auth_token_uri = urljoin(self._auth_url, self._auth_token)
        uri = urljoin(self._get_rdp_url_root(), auth_token_uri)
        return uri

    def get_omm_login_message_key_data(self):
        return self._connection.get_omm_login_message_key_data()

    def get_rdp_login_message(self, stream_id):
        return {
            "streamID": f"{stream_id:d}",
            "method": "Auth",
            "token": self._access_token,
        }

    async def open_async(self):
        def open_state():
            self._state = OpenState.Open
            self._on_state(self._state, "Session is opened.")

        if self._state in [OpenState.Pending, OpenState.Open]:
            return self._state

        self._connection.open()
        open_state()
        await self._connection.waiting_for_stream_ready(open_state)

        #   done, return state
        return self._state

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
        return await self._connection.http_request_async(
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

    def __repr__(self):
        return create_repr(
            self,
            middle_path="session.platform",
            content=f"{{session_name='{self.name}'}}",
        )
