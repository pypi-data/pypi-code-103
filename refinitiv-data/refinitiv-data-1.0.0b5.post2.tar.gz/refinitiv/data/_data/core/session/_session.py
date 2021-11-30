# coding: utf-8

__all__ = ["Session", "DacsParams"]

import abc
import asyncio
import itertools
import logging
import socket
import traceback
import warnings
from enum import Enum, unique
from threading import Lock
from typing import Callable, TYPE_CHECKING

from .tools import is_closed

import httpx
import nest_asyncio
from refinitiv.data._data.vendor import requests_async
import urllib3.exceptions

from ._session_cxn_type import SessionCxnType
from ...open_state import OpenState

from ._timeout_adapter import TimeoutRetry, AsyncHTTPAdapter
from ... import configure
from ... import log
from ...tools import cached_property, DEBUG
from ...tools import create_repr

if TYPE_CHECKING:
    from . import SessionConnection
    from ...configure import _RDPConfig

# Load nest_asyncio to allow multiple calls to run_until_complete available
nest_asyncio.apply()


def get_http_request_timeout_secs(session):
    """the default http request timeout in secs"""
    key = configure.keys.http_request_timeout
    value = session.config.get(key)

    is_list = isinstance(value, list)
    if is_list and len(value) == 1:
        value = value[0]
        try:
            value = int(value)
        except ValueError:
            pass

    number = isinstance(value, int) or isinstance(value, float)
    negative_number = number and value < 0

    if number and value == 0:
        value = None
    elif number and value == 1:
        value = 1

    is_none = value is None

    set_default = not is_none and (not number or negative_number)
    print_warn = not is_none and (not number or negative_number)

    if set_default:
        value = configure.defaults.http_request_timeout

    if print_warn:
        session.warning(f"Invalid value of the {key}. Default value is used")

    return value


class DacsParams(object):
    def __init__(self, *args, **kwargs):
        self.deployed_platform_username = kwargs.get(
            "deployed_platform_username", "user"
        )
        self.dacs_application_id = kwargs.get("dacs_application_id", "256")
        self.dacs_position = kwargs.get("dacs_position")
        if self.dacs_position in [None, ""]:
            try:
                position_host = socket.gethostname()
                self.dacs_position = "{}/{}".format(
                    socket.gethostbyname(position_host), position_host
                )
            except socket.gaierror:
                self.dacs_position = "127.0.0.1/net"
        self.authentication_token = kwargs.get("authentication_token")


class Session(abc.ABC):
    _DUMMY_STATUS_CODE = -1
    _id_iterator = itertools.count()
    # Logger for messages outside of particular session instances
    class_logger = log.create_logger("session")

    @unique
    class EventCode(Enum):
        """
        Each session can report different status events during it's lifecycle.
            StreamConnecting : Denotes the connection to the stream service within the session is pending.
            StreamConnected : Denotes the connection to the stream service has been successfully established.
            StreamDisconnected : Denotes the connection to the stream service is not established.
            SessionAuthenticationSuccess : Denotes the session has successfully authenticated this client.
            SessionAuthenticationFailed : Denotes the session has failed to authenticate this client.
            StreamAuthenticationSuccess: Denotes the stream has successfully authenticated this client.
            StreamAuthenticationFailed: Denotes the stream has failed to authenticate this client.
            DataRequestOk : The request for content from the session data services has completed successfully.
            DataRequestFailed : The request for content from the session data services has failed.
        """

        StreamConnecting = 1
        StreamConnected = 2
        StreamDisconnected = 3
        StreamAuthenticationSuccess = 4
        StreamAuthenticationFailed = 5
        StreamReconnecting = 6

        SessionConnecting = 21
        SessionConnected = 22
        SessionDisconnected = 23
        SessionAuthenticationSuccess = 24
        SessionAuthenticationFailed = 25
        SessionReconnecting = 26

        DataRequestOk = 61
        DataRequestFailed = 62

    __acquire_session_id_lock = Lock()

    @property
    def name(self):
        return self._name

    def __init__(
        self,
        app_key,
        on_state=None,
        on_event=None,
        token=None,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        name="default",
    ):
        with self.__acquire_session_id_lock:
            self._session_id = next(self._id_iterator)
        session_type = self.type.name.lower()
        logger_name = f"sessions.{session_type}.{name}.{self.session_id}"
        self.class_logger.debug(
            f'Creating session "{logger_name}" based on '
            f'session.{session_type}.Definition("{session_type}.{name}")'
        )

        if app_key is None:
            raise ValueError("app_key value can't be None")

        self._lock_log = Lock()

        self._state = OpenState.Closed
        self._status = Session.EventCode.StreamDisconnected
        self._last_event_code = None
        self._last_event_message = None

        self._last_stream_connection_name = None

        self._app_key = app_key
        self._on_event_callback = on_event
        self._on_state_callback = on_state
        self._access_token = token
        self._dacs_params = DacsParams()

        if deployed_platform_username:
            self._dacs_params.deployed_platform_username = deployed_platform_username
        if dacs_position:
            self._dacs_params.dacs_position = dacs_position
        if dacs_application_id:
            self._dacs_params.dacs_application_id = dacs_application_id

        self._logger = log.create_logger(logger_name)
        # redirect log method of this object to the log in logger object
        self.log = self._logger.log
        self.warning = self._logger.warning
        self.error = self._logger.error
        self.debug = self._logger.debug
        self.info = self._logger.info

        self._name = name

        # parameters for stream websocket
        try:
            self._loop = asyncio.get_event_loop()
            self.log(1, f"Session loop was set to current event loop {self._loop}")
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            self.log(1, f"Session loop was set with a new event loop {self._loop}")

        nest_asyncio.apply(self._loop)

        self.__lock_callback = Lock()
        self._httpx_async_client = None
        self._http_session_auto_retry_client = None

        # for service directory
        self._service_directories = []

        self._config: "_RDPConfig" = configure.get_config().copy()
        self._config.on(configure.ConfigEvent.UPDATE, self._on_config_updated)

    @cached_property
    def _connection(self) -> "SessionConnection":
        from ._session_cxn_factory import get_session_cxn

        cxn_type = self._get_session_cxn_type()
        cxn = get_session_cxn(cxn_type, self)
        self.debug(f"Created session connection {cxn_type}")
        return cxn

    @abc.abstractmethod
    def _get_session_cxn_type(self) -> SessionCxnType:
        pass

    def on_state(self, callback: Callable) -> None:
        """
        On state callback

        Parameters
        ----------
        callback: Callable
            Callback function or method

        Raises
        ----------
        Exception
            If user provided invalid object type
        """
        if not callable(callback):
            raise TypeError("Please provide callable object")

        self._on_state_callback = callback

    def get_on_state_callback(self) -> Callable:
        return self._on_state_callback

    def on_event(self, callback: Callable) -> None:
        """
        On event callback

        Parameters
        ----------
        callback: Callable
            Callback function or method

        Raises
        ----------
        Exception
            If user provided invalid object type
        """
        if not callable(callback):
            raise TypeError("Please provide callable object")

        self._on_event_callback = callback

    def get_on_event_callback(self) -> Callable:
        return self._on_event_callback

    def __repr__(self):
        return create_repr(
            self,
            middle_path="session",
            content=f"{{name='{self.name}'}}",
        )

    def _on_config_updated(self):
        log_level = log.read_log_level_config()

        if log_level != self.get_log_level():
            self.set_log_level(log_level)

    def run_until_complete(self, future):
        return self._loop.run_until_complete(future)

    def call_soon_threadsafe(self, callback, *args):
        return self._loop.call_soon_threadsafe(callback, *args)

    def has_same_loop(self, loop=None):
        cur_loop = asyncio.get_event_loop()
        loop = loop or cur_loop
        return self._loop == loop

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def config(self):
        return self._config

    @property
    def open_state(self):
        """
        Returns the session state.
        """
        return self._state

    def get_last_event_code(self):
        """
        Returns the last session event code.
        """
        return self._last_event_code

    def get_last_event_message(self):
        """
        Returns the last event message.
        """
        return self._last_event_message

    @property
    def app_key(self):
        """
        Returns the application id.
        """
        return self._app_key

    @app_key.setter
    def app_key(self, app_key):
        """
        Set the application key.
        """
        from ...legacy.tools import is_string_type

        if app_key is None:
            return
        if not is_string_type(app_key):
            raise AttributeError("application key must be a string")

        self._app_key = app_key

    def set_access_token(self, access_token):
        self._access_token = access_token

    def set_stream_auth_token(self, auth_token: str) -> None:
        from ...delivery.stream import stream_cxn_cache

        if stream_cxn_cache.has_cxns(self):
            cxns_by_session = stream_cxn_cache.get_cxns(self)
            for cxn in cxns_by_session:
                cxn.set_auth_token(auth_token)

    @property
    def session_id(self):
        return self._session_id

    def logger(self) -> logging.Logger:
        return self._logger

    def _get_rdp_url_root(self):
        return ""

    @cached_property
    def http_request_timeout_secs(self):
        return get_http_request_timeout_secs(self)

    ############################################################
    #   reconnection configuration

    @property
    def stream_auto_reconnection(self):
        return True

    @property
    def server_mode(self):
        return False

    @abc.abstractmethod
    def get_omm_login_message_key_data(self):
        """return the login message for OMM 'key' section"""
        pass

    @abc.abstractmethod
    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP protocol"""
        pass

    ######################################
    # methods to manage log              #
    ######################################
    def set_log_level(self, log_level: [int, str]) -> None:
        """
        Set the log level.
        By default, logs are disabled.

        Parameters
        ----------
        log_level : int, str
            Possible values from logging module :
            [CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET]
        """
        log_level = log.convert_log_level(log_level)
        self._logger.setLevel(log_level)

        if DEBUG:
            # Enable debugging
            self._loop.set_debug(True)

            # Make the threshold for "slow" tasks very very small for
            # illustration. The default is 0.1, or 100 milliseconds.
            self._loop.slow_callback_duration = 0.001

            # Report all mistakes managing asynchronous resources.
            warnings.simplefilter("always", ResourceWarning)

    def get_log_level(self):
        """
        Returns the log level
        """
        return self._logger.level

    def trace(self, message):
        self._logger.log(log.TRACE, message)

    ######################################
    # methods to open and close session  #
    ######################################
    def open(self) -> OpenState:
        """open session

        do an initialization config file, and http session if it's necessary.

        Returns
        -------
        OpenState
            the current state of this session.
        """
        if self._state in [OpenState.Pending, OpenState.Open]:
            # session is already opened or is opening
            return self._state
        self._config.remove_listener(
            configure.ConfigEvent.UPDATE, self._on_config_updated
        )
        self._config.on(configure.ConfigEvent.UPDATE, self._on_config_updated)

        # httpx has it's default Accept header and server wants application/json or nothing
        self._httpx_async_client = httpx.AsyncClient(
            headers={"Accept": "application/json"}
        )
        # Config for http auto-retry
        key = configure.keys.http_auto_retry_config
        auto_retry_config = self._config.get(key, None)
        if auto_retry_config:
            # currently, "enabled" is not yet exposed in auto-retry config, by default it's enabled
            auto_retry_enabled = True  # auto_retry_config.get("enabled", True)
            number_of_retries = auto_retry_config.get("number-of-retries", 3)
            retry_on_errors = auto_retry_config.get("on-errors", [])
            retry_backoff_factor = auto_retry_config.get("backoff-factor", 1)
            retry_on_methods = auto_retry_config.get("on-methods", ["GET", "POST"])

            self._http_session_auto_retry_client = requests_async.Session()
            retry_strategy = TimeoutRetry(
                session=self,
                timeout=self.http_request_timeout_secs,
                total=number_of_retries,
                status_forcelist=retry_on_errors,
                allowed_methods=retry_on_methods,
                backoff_factor=retry_backoff_factor,
            )

            adapter = AsyncHTTPAdapter(
                max_retries=retry_strategy, timeout=self.http_request_timeout_secs
            )
            self._http_session_auto_retry_client.mount("https://", adapter)
            self._http_session_auto_retry_client.mount("http://", adapter)
        else:
            auto_retry_enabled = False

        self._loop.run_until_complete(self.open_async())
        return self._state

    def close(self) -> OpenState:
        """
        Close platform/desktop session

        Returns
        -------
        State
        """
        if is_closed(self):
            return self._state

        if not self._loop.is_closed():
            return self._loop.run_until_complete(self.close_async())
        else:
            return self._close()

    @abc.abstractmethod
    async def open_async(self) -> OpenState:
        pass

    async def close_async(self) -> OpenState:
        from ...delivery.stream import stream_cxn_cache

        await stream_cxn_cache.close_cxns_async(self)

        if DEBUG:
            await asyncio.sleep(5)

            import threading

            self.debug(
                "Threads:\n\t" + "\n\t".join([str(t) for t in threading.enumerate()])
            )

            if stream_cxn_cache.has_cxns(self):
                raise AssertionError(
                    f"Not all cxns are closed (session={self},\n"
                    f"cxns={stream_cxn_cache.get_cxns(self)})"
                )

        return self._close()

    def _close(self) -> OpenState:
        self._state = OpenState.Closed
        self._connection.close()
        self._config.remove_listener(
            configure.ConfigEvent.UPDATE, self._on_config_updated
        )
        self._loop.run_until_complete(self._httpx_async_client.aclose())
        self._httpx_async_client = None

        if self._http_session_auto_retry_client:
            self._loop.run_until_complete(self._http_session_auto_retry_client.close())
            self._http_session_auto_retry_client = None

        return self._state

    ##########################################################
    # methods for session callbacks from streaming session   #
    ##########################################################
    def _on_open(self):
        with self.__lock_callback:
            self._state = OpenState.Pending

    def _on_close(self):
        with self.__lock_callback:
            self._state = OpenState.Closed

    def _on_state(self, state_code, state_text):
        with self.__lock_callback:
            if isinstance(state_code, OpenState):
                self._state = state_code
                if self._on_state_callback is not None:
                    try:
                        self._on_state_callback(self, state_code, state_text)
                    except Exception as e:
                        self.error(
                            f"on_state user function on session {self.session_id} raised error {e}"
                        )

    def _on_event(
        self,
        event_code,
        event_msg,
        streaming_session_id=None,
        stream_connection_name=None,
    ):
        self.debug(
            f"Session._on_event("
            f"event_code={event_code}, "
            f"event_msg={event_msg}, "
            f"streaming_session_id={streaming_session_id}, "
            f"stream_connection_name={stream_connection_name})"
        )
        with self.__lock_callback:
            #   check the on_event trigger from some of the stream connection or not?
            #   not stream connection on_event, just call the on_event callback
            #   call the callback function
            if self._on_event_callback:
                try:
                    self._on_event_callback(self, event_code, event_msg)
                except Exception as e:
                    self.error(
                        f"on_event user function on session {self.session_id} raised error {e}"
                    )

    ##############################################
    # methods for status reporting               #
    ##############################################
    @staticmethod
    def _report_session_status(self, session, session_status, event_msg):
        _callback = self._get_status_delegate(session_status)
        if _callback is not None:
            json_msg = self._define_results(session_status)[Session.CONTENT] = event_msg
            _callback(session, json_msg)

    def report_session_status(self, session, event_code, event_msg):
        # Report the session status event defined with the eventMsg to the appropriate delegate
        self._last_event_code = event_code
        self._last_event_message = event_msg
        _callback = self._get_status_delegate(event_code)
        if _callback is not None:
            try:
                _callback(session, event_code, event_msg)
            except Exception as e:
                self._session.error(
                    f"{self.__name__} on_event or on_state callback raised exception: {e!r}"
                )
                self._session.debug(f"{traceback.format_exc()}")

    def _get_status_delegate(self, event_code):
        _cb = None

        if event_code in [
            Session.EventCode.SessionAuthenticationSuccess,
            Session.EventCode.SessionAuthenticationFailed,
        ]:
            _cb = self._on_state_callback
        elif event_code not in [
            self.EventCode.DataRequestOk,
            self.EventCode.StreamConnecting,
            self.EventCode.StreamConnected,
            self.EventCode.StreamDisconnected,
        ]:
            _cb = self._on_event_callback
        return _cb

    ############################
    # methods for HTTP request #
    ############################
    async def _http_request_async(
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
        auto_retry = kwargs.pop("auto_retry", False)

        if method is None:
            method = "GET"

        if headers is None:
            headers = {}

        if self._access_token is not None:
            headers["Authorization"] = "Bearer {}".format(self._access_token)

        if closure is not None:
            headers["Closure"] = closure

        headers.update({"x-tr-applicationid": self.app_key})

        #   http request timeout
        if "timeout" not in kwargs:
            #   override using the http request timeout from config file
            http_request_timeout = self.http_request_timeout_secs
            kwargs["timeout"] = http_request_timeout

        self.debug(
            f"Request to {url}\n\tmethod = {method}\n\t"
            f"headers = {headers}\n\tparams = {params}\n\t"
            f"data = {data}\n\tjson = {json}"
        )

        if auto_retry:
            # if auto retry is True, use self._http_session_auto_retry_client to send request
            _http_request = requests_async.Request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                json=json,
            ).prepare()
            try:
                request_response = await self._http_session_auto_retry_client.send(
                    _http_request, **kwargs
                )

            except urllib3.exceptions.MaxRetryError as error:
                self.error(error)
                raise error

            except (
                requests_async.exceptions.RequestException,
                requests_async.exceptions.HTTPError,
                requests_async.exceptions.ConnectionError,
                requests_async.exceptions.TooManyRedirects,
                requests_async.exceptions.ConnectTimeout,
                requests_async.exceptions.FileModeWarning,
                requests_async.exceptions.ReadTimeout,
                requests_async.exceptions.Timeout,
                requests_async.exceptions.URLRequired,
            ) as error:
                self.error(
                    f"An error occurred while requesting {error.request.url!r}.\n\t{error!r}"
                )
                raise error
        else:
            # without auto_retry, use self._httpx_async_client to send request
            try:
                request_response = await self._httpx_async_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    json=json,
                    **kwargs,
                )
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.HTTPStatusError,
                httpx.InvalidURL,
                httpx.LocalProtocolError,
                httpx.NetworkError,
                httpx.ProtocolError,
                httpx.ProxyError,
                httpx.ReadError,
                httpx.RequestError,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
                httpx.TooManyRedirects,
                httpx.TransportError,
                httpx.TimeoutException,
            ) as error:
                self.error(
                    f"An error occurred while requesting {error.request.url!r}.\n\t{error!r}"
                )
                raise error

        assert request_response is not None
        self.debug(
            f"HTTP request response {request_response.status_code}: {request_response.text}"
        )
        return request_response

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
        return await self._http_request_async(
            url=url,
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

    def http_request(
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
        headers = headers or {}
        loop = loop or self._loop
        response = loop.run_until_complete(
            self.http_request_async(
                url=url,
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
        )
        return response


EventCode = Session.EventCode
