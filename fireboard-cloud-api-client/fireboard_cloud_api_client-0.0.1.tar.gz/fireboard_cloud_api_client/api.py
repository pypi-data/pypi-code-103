from typing import List
from aiohttp import (
    ClientSession,
    ClientResponseError,
    ClientConnectorError,
)
import logging
from typing import Any, Callable, List, Optional
from aiohttp.client_exceptions import ServerDisconnectedError

LOGGER = logging.getLogger(__name__)

class FireboardAPI:
    """Class that represents a Fireboard object in the Fireboard Cloud API."""

    def __init__(
        self,
        email: str,
        password: str,
        base_url: Optional[str] = "https://fireboard.io/api",
        session: Optional[ClientSession] = None,
    ):
        """Initialize a fireboard object."""
        self._base_url = base_url
        self._email = email
        self._password = password
        self._session = session
        self._token = None

    async def list_devices(self) -> List[dict]:
        """Fetch the data for all Fireboard devices associated with a token."""
        return await self.__request("get", "v1/devices.json")

    async def get_device(self, device_uuid: str) -> dict:
        """Fetch the data for a single Fireboard device."""
        return await self.__request("get", f"v1/devices/{device_uuid}.json")

    async def get_realtime_temperature(self, device_uuid: str) -> dict:
        """Read realtime temperatures for the device."""
        return await self.__request("get", f"v1/devices/{device_uuid}/temps.json")

    async def get_realtime_drivelog(self, device_uuid: str) -> dict:
        """Read realtime log of fireboard drive activity for the device."""
        return await self.__request("get", f"v1/devices/{device_uuid}/drivelog.json")

    async def list_sessions(self) -> dict:
        """Get all sessions in your account."""
        return await self.__request("get", f"v1/sessions.json")

    async def get_session(self, session_id: int) -> dict:
        """Retrieve detailed information about a specific session."""
        return await self.__request("get", f"v1/sessions/{session_id}.json")

    async def get_session_chart(self, session_id: int, drive: bool = False) -> dict:
        """Retrieve session information formatted for charting. Can optionally include drive information."""
        drive_param = "?drive=1" if drive else ""
        return await self.__request("get", f"v1/sessions/{session_id}/chart.json{drive_param}")
    

    async def __request(self, method: str, path: str, **kwargs) -> dict:
        async def tokenRequest(session: ClientSession) -> dict:
            headers = kwargs.get("headers")
            if headers is None:
                headers = {}
            else:
                headers = dict(headers)
            headers["Content-Type"] = "application/json"
            try:
                async with session.request(
                    "post",
                    f"{self._base_url}/rest-auth/login/",
                    headers=headers,
                    json={"username": self._email, "password": self._password},
                ) as authResp:
                    authResp.raise_for_status()
                    authData = await authResp.json()
                    self._token = authData["key"]
            except ClientResponseError as cre:
                if cre.status == 401:
                    raise FireboardApiAuthError(
                        "error getting token, check your credentials"
                    )
                elif cre.status < 500:
                    raise FireboardApiClientError(
                        f"client error, got: {cre.status} {cre.message}"
                    )
                else:
                    raise FireboardApiServerError(
                        f"server error, got: {cre.status} {cre.message}"
                    )
            except ClientConnectorError as cce:
                raise FireboardApiConnectionError(cce.message)

        async def request(session: ClientSession) -> dict:
            headers = kwargs.get("headers")
            if headers is None:
                headers = {}
            else:
                headers = dict(headers)
            headers["Content-Type"] = "application/json"
            headers["Authorization"] = f"Token {self._token}"
            async with session.request(
                method, f"{self._base_url}/{path}", **kwargs, headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()

        if not self._token:
            await self.__call(tokenRequest)

        return await self.__call(request)

    async def __call(self, handler: Callable[[ClientSession], Any]):
        if not self._session:
            async with ClientSession() as request_session:
                return await handler(request_session)
        else:
            try:
                return await handler(self._session)
            except ServerDisconnectedError:
                return await handler(self._session)


class FireboardApiError(Exception):
    """Exception base class"""

    def __init__(self, message: str):
        self.message = message


class FireboardApiAuthError(FireboardApiError):
    """Exception raised when there is an authentication error (401)"""

    def __init__(self, message: str):
        super().__init__(message)


class FireboardApiClientError(FireboardApiError):
    """Exception raised when there is an 40x error other than a 401"""

    def __init__(self, message: str):
        super().__init__(message)


class FireboardApiServerError(FireboardApiError):
    """Exception raised when there is an 50x error"""

    def __init__(self, message: str):
        super().__init__(message)


class FireboardApiConnectionError(FireboardApiError):
    """Exception raised when there is an 50x error"""

    def __init__(self, message: str):
        super().__init__(message)
