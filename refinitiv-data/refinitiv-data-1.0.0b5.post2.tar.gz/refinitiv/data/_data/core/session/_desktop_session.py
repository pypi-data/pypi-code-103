# coding: utf-8

__all__ = ["DesktopSession"]

import logging
import socket

import httpx
from appdirs import user_config_dir, user_data_dir

from ._session import Session
from ._session_cxn_type import SessionCxnType
from ...open_state import OpenState
from ._session_type import SessionType
from ... import __version__
from ...errors import DesktopSessionError
from ...tools import urljoin


class DesktopSession(Session):
    type = SessionType.DESKTOP

    def __init__(
        self,
        app_key,
        on_state=None,
        on_event=None,
        name="default",
        base_url=None,
        platform_path_rdp=None,
        platform_path_udf=None,
        handshake_url=None,
        token=None,
        dacs_position=None,
        dacs_application_id=None,
    ):

        super().__init__(
            app_key=app_key,
            on_state=on_state,
            on_event=on_event,
            token=token,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            name=name,
        )
        from os import getenv

        self._port = None
        self._udf_url = None
        self._timeout = self.http_request_timeout_secs

        # Detect DP PROXY url from CODEBOOK environment to manage multi user mode
        self._dp_proxy_base_url = getenv("DP_PROXY_BASE_URL")
        if self._dp_proxy_base_url:
            self._base_url = self._dp_proxy_base_url
        else:
            self._base_url = base_url

        self._platform_path_rdp = platform_path_rdp
        self._platform_path_udf = platform_path_udf
        self._handshake_url = handshake_url
        #   a mapping the stream connection status
        self._stream_connection_name_to_status = {}

        #   uuid is retrieved in CODEBOOK environment, it's used for DP-PROXY to manage multi-user mode
        self._uuid = getenv("REFINITIV_AAA_USER_ID")

        self._logger.debug(
            "".join(
                [
                    f"DesktopSession created with following parameters:",
                    f' app_key="{app_key}", name="{name}"',
                    f' base_url="{base_url}"' if base_url is not None else "",
                    f' platform_path_rdp="{platform_path_rdp}"'
                    if platform_path_rdp
                    else "",
                    f' platform_path_udf="{platform_path_udf}"'
                    if platform_path_udf
                    else "",
                    f' handshake_url="{handshake_url}"' if handshake_url else "",
                ]
            )
        )

    def _get_session_cxn_type(self) -> SessionCxnType:
        return SessionCxnType.DESKTOP

    def _get_udf_url(self):
        """
        Returns the url to request data to udf platform.
        """
        return urljoin(self._base_url, self._platform_path_udf)

    def _get_handshake_url(self):
        """
        Returns the url to handshake with the proxy.
        """
        return urljoin(self._base_url, self._handshake_url)

    def _get_base_url(self):
        return self._base_url

    def _get_rdp_url_root(self):
        if self._platform_path_rdp is None:
            raise ValueError(
                f"Can't find '{self.name}.platform-paths.rdp' "
                f"in config file. Please add this attribute."
            )
        url = urljoin(self._base_url, self._platform_path_rdp)
        return url

    def set_timeout(self, timeout):
        """
        Set the timeout for requests.
        """
        self._timeout = timeout

    def get_timeout(self):
        """
        Returns the timeout for requests.
        """
        return self._timeout

    def set_port_number(self, port_number, logger=None):
        """
        Set the port number to reach Desktop API proxy.
        """
        self._port = port_number
        if port_number:
            try:
                protocol, path, default_port = self._base_url.split(":")
            except ValueError:
                protocol, path, *_ = self._base_url.split(":")
                default_port = ""

            try:
                url = ":".join([protocol, path, str(self._port)])
            except TypeError:
                url = ":".join([protocol, path, default_port])

            self._base_url = url
            self.close()
        else:
            self._udf_url = None

        if logger:
            logger.info(f"Set Proxy port number to {self._port}")

    def get_port_number(self):
        """
        Returns the port number
        """
        return self._port

    ############################################################
    #   multi-websockets support

    def get_omm_login_message_key_data(self):
        """return the login message for OMM 'key' section"""
        return {
            "Elements": {
                "AppKey": self.app_key,
                "ApplicationId": self._dacs_params.dacs_application_id,
                "Position": self._dacs_params.dacs_position,
                "Authorization": f"Bearer {self._access_token}",
            }
        }

    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP"""
        return {
            "method": "Auth",
            "streamID": f"{stream_id:d}",
            "appKey": self.app_key,
            "authorization": f"Bearer {self._access_token}",
        }

    #######################################
    #  methods to open and close session  #
    #######################################
    def open(self):
        if self._state in [OpenState.Pending, OpenState.Open]:
            return self._state

        return super(DesktopSession, self).open()

    ############################################
    #  methods to open asynchronously session  #
    ############################################
    async def open_async(self):
        def close_state(msg):
            self._state = OpenState.Closed
            self._on_event(Session.EventCode.SessionAuthenticationFailed, msg)
            self._on_state(self._state, "Session is closed.")

        if self._state in [OpenState.Pending, OpenState.Open]:
            return self._state

        self._connection.open()

        error = None
        try:
            if not self._dp_proxy_base_url:
                # Identify port number to update base url
                port_number = await self.identify_scripting_proxy_port()
                self.set_port_number(port_number)

            handshake_url = self._get_handshake_url()
            await self.handshake(handshake_url)

        except DesktopSessionError as e:
            self.error(e.message)
            error = e

        if not error:
            self.debug(f"Application ID: {self.app_key}")
            self._state = OpenState.Open
            self._on_state(self._state, "Session is opened.")

        not self._dp_proxy_base_url and not port_number and close_state(
            "Eikon is not running"
        )
        error and close_state(error.message)
        await super(DesktopSession, self).open_async()
        return self._state

    @staticmethod
    def read_firstline_in_file(filename, logger=None):
        try:
            f = open(filename)
            first_line = f.readline()
            f.close()
            return first_line
        except IOError as e:
            if logger:
                logger.error(f"I/O error({e.errno}): {e.strerror}")
            return ""

    async def identify_scripting_proxy_port(self):
        """
        Returns the port used by the Scripting Proxy stored in a configuration file.
        """
        import platform
        import os

        port = None
        path = []
        app_names = ["Data API Proxy", "Eikon API proxy", "Eikon Scripting Proxy"]
        for app_author in ["Refinitiv", "Thomson Reuters"]:
            if platform.system() == "Linux":
                path = path + [
                    user_config_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(
                        user_config_dir(app_name, app_author, roaming=True)
                    )
                ]
            else:
                path = path + [
                    user_data_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(user_data_dir(app_name, app_author, roaming=True))
                ]

        if len(path):
            port_in_use_file = os.path.join(path[0], ".portInUse")

            # Test if ".portInUse" file exists
            if os.path.exists(port_in_use_file):
                # First test to read .portInUse file
                first_line = self.read_firstline_in_file(port_in_use_file)
                if first_line != "":
                    saved_port = first_line.strip()
                    test_proxy_url = self._update_port_in_url(
                        self._base_url, saved_port
                    )
                    test_proxy_result = await self.check_proxy(test_proxy_url)
                    if test_proxy_result:
                        port = saved_port
                        self.debug(f"Port {port} was retrieved from .portInUse file")

        if port is None:
            self.info(
                "Warning: file .portInUse was not found. Try to fallback to default port number."
            )
            port_list = ["9000", "36036"]
            for port_number in port_list:
                self.info(f"Try defaulting to port {port_number}...")
                test_proxy_url = self._update_port_in_url(self._base_url, port_number)
                test_proxy_result = await self.check_proxy(test_proxy_url)
                if test_proxy_result:
                    port = port_number
                    self._port = port
                    self.info(f"Default proxy port {port} was successfully checked")

        if port is None:
            self.error(
                "Error: no proxy address identified.\nCheck if Desktop is running."
            )
            return None

        return port

    async def check_proxy(self, url: str, timeout=None) -> bool:

        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout

        url = urljoin(url, "/api/status")

        try:
            response = await self._http_request_async(
                url=url,
                method="GET",
                timeout=timeout,
            )

            self.debug(
                f"Checking proxy url {url} response : {response.status_code} - {response.text}"
            )
            return True
        except (socket.timeout, httpx.ConnectTimeout):
            self.log(logging.INFO, f"Timeout on checking proxy url {url}")
        except ConnectionError as e:
            self.log(logging.INFO, f"Connexion Error on checking proxy {url} : {e!r}")
        except Exception as e:
            self.debug(f"Error on checking proxy url {url} : {e!r}")
        return False

    async def handshake(self, url, timeout=None):
        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout

        self.debug(f"Try to handshake on url {url}...")
        try:
            # DAPI for E4 - API Proxy - Handshake
            _body = {
                "AppKey": self.app_key,
                "AppScope": "trapi",
                "ApiVersion": "1",
                "LibraryName": "RDP Python Library",
                "LibraryVersion": __version__,
            }

            if self._uuid:
                # add uuid for DP-PROXY multi user mode
                _body.update({"Uuid": self._uuid})

            _headers = {"Content-Type": "application/json"}

            response = None
            try:
                response = await self._http_request_async(
                    url=url,
                    method="POST",
                    headers=_headers,
                    json=_body,
                    timeout=timeout,
                )

                self.debug(f"Response : {response.status_code} - {response.text}")
            except Exception as e:
                self.log(1, f"HTTP request failed: {e!r}")

            if response:
                if response.status_code == httpx.codes.OK:
                    result = response.json()
                    self._access_token = result.get("access_token", None)

                elif response.status_code == httpx.codes.BAD_REQUEST:
                    self.error(
                        f"Status code {response.status_code}: "
                        f"Bad request on handshake url {url} : {response.text}"
                    )
                    key_is_incorrect_msg = (
                        f"Status code {response.status_code}: App key is incorrect"
                    )
                    self._on_event(
                        Session.EventCode.SessionAuthenticationFailed,
                        key_is_incorrect_msg,
                    )
                    raise DesktopSessionError(1, key_is_incorrect_msg)
                else:
                    self.debug(
                        f"Response {response.status_code} on handshake url {url} : {response.text}"
                    )

        except (socket.timeout, httpx.ConnectTimeout):
            raise DesktopSessionError(1, f"Timeout on handshake url {url}")
        except Exception as e:
            raise DesktopSessionError(1, f"Error on handshake url {url} : {e!r}")
        except DesktopSessionError as e:
            raise e

    @staticmethod
    def _update_port_in_url(url, port):
        try:
            protocol, path, default_port = url.split(":")
        except ValueError:
            protocol, path, *_ = url.split(":")

        if port is not None:
            retval = ":".join([protocol, path, str(port)])
        else:
            retval = url

        return retval
