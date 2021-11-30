# coding: utf-8

import asyncio
import collections
import threading
import time
from typing import TYPE_CHECKING

import httpx

from .grant_password import GrantPassword
from .grant_refresh import GrantRefreshToken

if TYPE_CHECKING:
    from . import Session


class AuthenticationTokenHandlerThread(threading.Thread):
    AuthenticationTokenInformation = collections.namedtuple(
        "AuthenticationTokenInformation",
        ["access_token", "expires_in", "refresh_token", "scope", "token_type"],
    )

    def __init__(
        self,
        session,
        grant,
        authentication_endpoint_url: str,
        server_mode: bool = None,
        take_exclusive_sign_on_control=None,
    ):
        threading.Thread.__init__(self, name="AuthenticationTokenHandlerThread")

        self._session: "Session" = session
        self._grant = grant

        self._authentication_endpoint_url = authentication_endpoint_url

        self._server_mode = False if server_mode is None else server_mode
        if self._server_mode and not self.is_password_grant():
            self._session.warning(
                "Server-mode is disabled "
                "because the grant type is not a password grant."
            )
        self._session.debug(f"\tserver-mode : {self._server_mode}")

        self._take_exclusive_sign_on_control = (
            True if take_exclusive_sign_on_control is None else False
        )

        self._request_new_authentication_token_event = threading.Event()
        self._start_event = threading.Event()
        self._stop_event = threading.Event()
        self._ready = threading.Event()
        self._error = threading.Event()

        self._last_exception = None

        self._token_expires_in_secs = None
        self._token_requested_time = None

    @property
    def last_exception(self):
        return self._last_exception

    def is_error(self):
        return self._error.is_set()

    def is_password_grant(self):
        return isinstance(self._grant, GrantPassword)

    def run(self):
        try:
            self._session.debug(f"STARTING :: {self.name}.run()")
            self._start_event.set()

            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            self._authorize()
            self._ready.set()

            debug_refresh_token_printing_time = time.time()
            while not self._stop_event.is_set():
                assert (
                    self._authentication_token_information is not None
                    and self._token_expires_in_secs is not None
                    and self._token_requested_time is not None
                ), "ERROR!!! Something is wrong in the _request_refresh_token function."

                now = time.time()
                if debug_refresh_token_printing_time < now:
                    delay = (
                        self._token_requested_time + self._token_expires_in_secs - now
                    )
                    self._session.debug(
                        f"    now                   = {now}\n    "
                        f"token_requested_time  = {self._token_requested_time}\n    "
                        f"token_expires_in_secs = {self._token_expires_in_secs}\n   "
                        f" delay                 = {delay}"
                    )
                    debug_refresh_token_printing_time = (
                        now + self._token_expires_in_secs / 6.5
                    )

                if now > self._token_requested_time + (
                    self._token_expires_in_secs // 2
                ):
                    self._request_new_authentication_token_event.set()
                else:
                    self._request_new_authentication_token_event.wait(1)

                if self._request_new_authentication_token_event.is_set():
                    self._request_refresh_token()
                    self._request_new_authentication_token_event.clear()
                    self._ready.set()

            self._session.debug(f"STOPPED :: {self.name}.run()")

        except Exception as e:
            self._session.error(
                f"ERROR!!! authentication handler raise an exception.\n{e!r}"
            )

            self._error.set()
            self._last_exception = e

        self._loop.close()

    def stop(self):
        if self._start_event.is_set():
            self._stop_event.set()
            self.join()

        self._session.debug("Authentication token handler thread STOPPED.")

    def wait_for_authorize_ready(self, timeout_secs=None):
        timeout_secs = 5 if timeout_secs is None else timeout_secs
        self._ready.wait(timeout_secs) or self._error.wait(timeout_secs)

    def authorize(self):
        self._session.debug(f"{self.name}.authorize()")
        assert (
            not self.is_error()
        ), f"AuthenticationTokenHandlerThread has an error.\n{self._last_exception}"

        self._ready.clear()

        if not self._start_event.is_set():
            assert (
                not self.is_alive()
            ), "ERROR!!! authentication thread has been started."
            self._session.debug("starting the authentication thread.........")
            self.start()
        else:
            self._session.debug("requesting a new authentication token........")
            self._request_new_authentication_token_event.set()

    def _authorize(self):
        if isinstance(self._grant, GrantPassword):
            (response, token_information) = self._request_token_by_password(
                client_id=self._session.app_key,
                username=self._grant.get_username(),
                password=self._grant.get_password(),
                scope=self._grant.get_token_scope(),
                take_exclusive_sign_on_control=True,
            )
        elif isinstance(self._grant, GrantRefreshToken):
            (response, token_information) = self._request_token_by_refresh_token(
                client_id=self._session.app_key,
                username=self._grant.get_username(),
                refresh_token=self._grant.get_refresh_token(),
            )
        else:
            error_message = f"ERROR!!! unknown grant type {self._grant}"
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )
            raise KeyError("ERROR!!! invalid grant type")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            error_message = f"ERROR!!! response {e.response.status_code} while requesting {e.request.url!r}."
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )
            raise e

        self._session.report_session_status(
            self._session,
            self._session.EventCode.SessionAuthenticationSuccess,
            "Successfully authorized to RDP authentication endpoint.",
        )
        self._authentication_token_information = token_information
        self._schedule_next_request_refresh_token(token_information)
        self._update_authentication_access_token(token_information.access_token)

    def _update_authentication_access_token(self, access_token):
        self._session.debug(
            f"{self.name}._update_authentication_access_token("
            f"access_token={access_token})"
        )
        self._session.set_access_token(access_token)
        self._session.set_stream_auth_token(access_token)

    def _schedule_next_request_refresh_token(self, token_information):
        self._session.debug(f"{self.name}._schedule_next_request_refresh_token()")
        self._token_expires_in_secs = float(token_information.expires_in)
        self._session.debug(
            f"\ta refresh token will be expired in {self._token_expires_in_secs} secs"
        )

    def _request_refresh_token(self):
        self._session.debug(f"{self.name}._request_refresh_token()")
        refreshed_token_information = None
        response = None
        while True:
            try:
                (
                    response,
                    refreshed_token_information,
                ) = self._request_token_by_refresh_token(
                    client_id=self._session.app_key,
                    username=self._grant.get_username(),
                    refresh_token=self._authentication_token_information.refresh_token,
                )
            except httpx.RequestError as e:
                self._session.error(
                    f"An error occurred while requesting {e.request.url!r}. with : {e}"
                )
                self._session.debug(f"\ttry to send a refresh token again.")
                time.sleep(1)
                continue

            except Exception as e:
                self._session.error(
                    f"Something wrong while requesting a refresh token.\n{e}"
                )
                self._session.debug(f"\ttry to refresh a token again.")
                time.sleep(1)
                continue

            else:
                break

        if response is not None and not response.is_error:
            self._session.info(
                "Successfully refresh an authentication token..........."
            )

        else:
            if self._server_mode and self.is_password_grant():
                self._session.debug(
                    "Server mode is enable, "
                    "retry by request token by password if it cannot refresh token."
                )
                while True:
                    time.sleep(1)
                    assert isinstance(
                        self._grant, GrantPassword
                    ), "It is not a GrantPassword, so we cannot re-authorize with authentication server."
                    try:
                        (
                            response,
                            refreshed_token_information,
                        ) = self._request_token_by_password(
                            client_id=self._session.app_key,
                            username=self._grant.get_username(),
                            password=self._grant.get_password(),
                            scope=self._grant.get_token_scope(),
                            take_exclusive_sign_on_control=self._take_exclusive_sign_on_control,
                        )
                    except httpx.RequestError as e:
                        self._session.error(
                            f"An error occurred while requesting {e.request.url!r} with : {e}"
                        )
                        self._session.debug(f"          try request token again.")
                        continue

                    except Exception as e:
                        self._session.error(
                            f"Something wrong while requesting a new token by username/password.\n   {e}"
                        )
                        self._session.debug(
                            f"\ttry request token again with username/password again."
                        )
                        time.sleep(1)
                        continue

                    if not response.is_error:
                        message = (
                            "Successfully refresh an authentication token..........."
                        )
                        self._session.info(message)
                        self._session.report_session_status(
                            self._session,
                            self._session.EventCode.SessionAuthenticationSuccess,
                            message,
                        )

                        #   done
                        break

                    if 400 <= response.status_code < 500:
                        self._session.error(
                            "ERROR!!! FAILED to refresh an authentication token..........."
                        )
                        error_message = f"ERROR!!! FAILED refresh an authentication token with response [{response.status_code}] {response.text} while requesting {response.url!r}."
                        self._session.error(error_message)
                        self._session.report_session_status(
                            self._session,
                            self._session.EventCode.SessionAuthenticationFailed,
                            error_message,
                        )

                    else:
                        assert (
                            500 <= response.status_code < 600
                        ), "Received the server error after request a new authorization to authentication server."

            else:
                error_message = f"ERROR!!! request a new refresh token has been failed.\nThe server-mode is disabled, so we do not re-authorize with username/password."
                self._session.error(error_message)
                self._session.report_session_status(
                    self._session,
                    self._session.EventCode.SessionAuthenticationFailed,
                    error_message,
                )
                raise ValueError(error_message)

        assert (
            refreshed_token_information is not None
        ), "ERROR!!! Something is wrong in the above _request_refresh_token function."

        self._authentication_token_information = refreshed_token_information

        self._schedule_next_request_refresh_token(refreshed_token_information)

        self._update_authentication_access_token(
            refreshed_token_information.access_token
        )

    def _request_token_by_password(
        self,
        client_id: str,
        username: str,
        password: str,
        scope: str,
        take_exclusive_sign_on_control: bool,
    ):
        request_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        request_data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": username,
            "password": password,
            "scope": scope,
            "takeExclusiveSignOnControl": take_exclusive_sign_on_control,
        }

        self._session.debug(
            f"Send a token request to {self._authentication_endpoint_url}"
        )
        self._session.debug(
            f"{{ "
            f"'grant_type' : 'password',\n"
            f"'client_id' : *********{client_id[-4:]},\n"
            f"'username' : {username},\n"
            f"'password' : *********,\n"
            f"'scope' : {scope},\n"
            f"'takeExclusiveSignOnControl' : {take_exclusive_sign_on_control} "
            f"}}"
        )

        (response, token_information) = self.__request_token(
            request_header, request_data
        )

        return (response, token_information)

    def _request_token_by_refresh_token(
        self, client_id: str, username: str, refresh_token: str
    ):
        assert (
            self._authentication_token_information.access_token is not None
        ), "AuthenticationTokenHandlerThread._request_token_by_refresh_token() does not have a refresh token."
        request_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        request_data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "username": username,
            "refresh_token": refresh_token,
        }

        self._session.debug(
            f"Send a token request to {self._authentication_endpoint_url}"
        )
        self._session.debug(
            f"{{ "
            f"'grant_type' : 'refresh_token',\n"
            f"'client_id' : *********{client_id[-4:]},\n"
            f"'username' : {username},\n"
            f"'refresh_token' : *********{refresh_token[-4:]}\n "
            f"}}"
        )

        (response, token_information) = self.__request_token(
            request_header, request_data
        )

        return (response, token_information)

    def __request_token(self, request_header, request_data):
        """request the token to authentication endpoint

        Raise
        ---------
            httpx.RequestError
                if cannot request the the authentication endpoint

            httpx.HTTPStatusError
                if the response is 4xx or 5xx.
        """

        self._token_requested_time = time.time()

        #   do request async to http server
        with httpx.Client() as client:
            response = client.request(
                method="POST",
                url=self._authentication_endpoint_url,
                headers=request_header,
                data=request_data,
                timeout=self._session.http_request_timeout_secs,
            )

        assert (
            response is not None
        ), "AuthenticationTokenHandlerThread.__request_token() got a None response."
        self._session.debug(f"HTTP response {response.status_code}: {response.text}")

        headers = response.headers
        if "Content-Type" in headers and "/json" in headers.get("Content-Type"):
            (response, token_information) = self._parse_request_token_response(response)
        else:
            error_message = f"ERROR!!! Invalid response content type only accept /json.\n      response = {response.content}."
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )
            raise ValueError(error_message)

        #   successfully request token
        return (response, token_information)

    def _parse_request_token_response(self, response):
        """parse the response data from the token request

        response example:

        Ok
            {
                "access_token": "string",
                "expires_in": "string",
                "refresh_token": "string",
                "scope": "string",
                "token_type": "string"
            }

        Error

            {
                "error": "string",
                "error_description": "string",
                "error_uri": "string"
            }

        """

        #   check the response successfully or not?
        if not response.is_error:
            #   successfully request a new token
            #   extract the response
            response_data = response.json()

            self._session.debug("Successfully request a new token......")
            self._session.debug(f"           Token requested response {response_data}")

            assert (
                "access_token" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "access_token" not in response'
            assert (
                "expires_in" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "expires_in" not in response'
            assert (
                "scope" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "scope" not in response'
            assert (
                "token_type" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "token_type" not in response'

            return (
                response,
                self.AuthenticationTokenInformation(
                    access_token=response_data["access_token"],
                    expires_in=response_data["expires_in"],
                    refresh_token=response_data.get("refresh_token", None),
                    scope=response_data["scope"],
                    token_type=response_data["token_type"],
                ),
            )

        else:
            self._session.error("ERROR!!! Failed to request a new token......")
            self._session.error(f"\tToken requested error {response.content}")
            return (response, None)
