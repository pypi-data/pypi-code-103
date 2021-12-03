"""Vconnex API."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from types import SimpleNamespace
from typing import Any

import requests

API__TOKEN = "/auth/project-token"

LOGGER = logging.getLogger(__name__)


class TokenInfo:
    """Token Info."""

    def __init__(self, token_resp: dict[str, Any]) -> None:
        """Create Token Info object."""
        self.token = token_resp.get("token")
        self.expire_time = token_resp.get("expireTime", 0)
        self.data = token_resp.get("data")


class ApiResponse(SimpleNamespace):
    """Api Response."""

    code: int
    msg: str
    data: Any


class ReturnCode:
    """Return Code."""

    SUCCESS = 1
    ERROR = 2
    NOT_FOUND = 15


class VconnexAPI:
    """VconnexAPI."""

    def __init__(
        self,
        endpoint: str,
        client_id: str,
        client_secret: str,
        project_code: str = None,
        lang: str = "vi",
    ) -> None:
        """Create VconnexAPI object."""
        self.session = requests.session()

        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.lang = lang
        self.project_code = project_code

        self.token_info: TokenInfo = None

    def __sign(
        self,
        algorithm: str,
        method: str,
        path: str,
        params: dict[str, Any] = None,
        body: dict[str, Any] = None,
    ) -> str:
        """Sign"""

        # Method
        str_to_sign = method
        str_to_sign += "\n"

        # Header
        str_to_sign += "\n"

        # URL
        str_to_sign += path

        if params is not None and len(params.keys()) > 0:
            str_to_sign += "?"
            params_keys = sorted(params.keys())
            query_builder = "".join(f"{ key}={params[key] }&" for key in params_keys)
            str_to_sign += query_builder[:-1]
        str_to_sign += "\n"

        # Body
        str_to_sign += (
            ""
            if body is None or len(body.keys()) == 0
            else json.dumps(body, separators=(",", ":"))
        )

        # Sign
        now_ts = int(time.time() * 1000)

        message = self.client_id
        if self.token_info is not None:
            message += self.token_info.token
        message += str(now_ts) + str_to_sign

        digestmod = hashlib.md5
        if algorithm == "SHA-256":
            digestmod = hashlib.sha256
        elif algorithm == "SHA-512":
            digestmod = hashlib.sha512

        sign = hmac.new(
            self.client_secret.encode("utf8"),
            msg=message.encode("utf8"),
            digestmod=digestmod,
        ).hexdigest()
        sign = base64.b64encode(f"{algorithm}.{now_ts}.{sign}".encode("utf8"))
        return sign

    def __get_token_info(self) -> TokenInfo:
        """Get exist token or retrieve new one"""
        if self.token_info is None or self.token_info.expire_time < (
            (int(time.time()) - 120) * 1000
        ):
            self.token_info = None
            try:
                resp = self.post(
                    API__TOKEN,
                    {
                        "clientId": self.client_id,
                        "clientSecret": self.client_secret,
                        "projectCode": self.project_code,
                    },
                )

                if resp is not None and resp.code == ReturnCode.SUCCESS:
                    self.token_info = TokenInfo(resp.data)
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Error while request token.")

        return self.token_info

    def __request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] = None,
        body: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Request base"""
        token_info = None if path.startswith(API__TOKEN) else self.__get_token_info()

        headers = {}
        if self.token_info is not None:
            # sign = self.__sign("SHA-256", method, path, params, body)
            sign = ""
            headers = {
                "X-Authorization": token_info.token,
                "sign": sign,
                "lang": self.lang,
            }
        elif path.startswith(API__TOKEN) is False:
            LOGGER.error("Unauthorized request")
            return None

        logging.debug(
            "Request: method=%s, url=%s, params=%s, body=%s, t=%d",
            method,
            self.endpoint + path,
            params,
            body,
            int(time.time() * 1000),
        )

        response = self.session.request(
            method, self.endpoint + path, params=params, json=body, headers=headers
        )

        if response.ok is False:
            LOGGER.error(
                "Response error: code=%d, body=%s",
                response.status_code,
                response.content,
            )
            return None

        result = ApiResponse(**response.json())

        LOGGER.debug(
            "Response: %s",
            json.dumps(
                result.__dict__ if hasattr(result, "__dict__") else result,
                ensure_ascii=False,
                indent=2,
            ),
        )

        return result

    def is_valid(self) -> bool:
        """Validate"""
        token_info = self.__get_token_info()
        return token_info is not None

    def get_token_data(self):
        """Get token data"""
        token_info = self.__get_token_info()
        return token_info.data if token_info is not None else None

    def get(self, path: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Get request."""
        return self.__request("GET", path, params, None)

    def post(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        """Post request."""
        return self.__request("POST", path, None, body)

    def put(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        """Put request."""
        return self.__request("PUT", path, None, body)

    def delete(self, path: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Delete request."""
        return self.__request("DELETE", path, params, None)
