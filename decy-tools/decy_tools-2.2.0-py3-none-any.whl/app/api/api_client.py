import sys
import json
from requests import Session
from threading import RLock
from functools import cached_property
from copy import deepcopy
from os.path import join
from os import getenv
from app.utils.logger.logging_utils import get_logger
from app.utils.exceptions import EnvVarMissing


class ApiClient:
    def __init__(self, logger=None):
        self._logger = logger or get_logger()
        self._API_BASE_PATH = "https://eu8w4cyyy8.execute-api.us-east-1.amazonaws.com/"
        self._AUTH_HEADER_KEY = "header_auth"
        self._BASE_HEADERS = {"Content-Type": "application/json"}

    @cached_property
    def api_key(self):
        key_name = "DECY_GATEWAY_TOKEN"
        key = getenv(key_name)
        if not key or key == "":
            self._logger.critical(
                f"Empty environment variable: {key_name} . This is needed to authenticate."
                "Please set. See ITG for the key."
            )
            sys.exit(1)
        else:
            return key

    @cached_property
    def _session(self):
        with RLock():
            session = Session()
            headers = deepcopy(self._BASE_HEADERS)
            headers[self._AUTH_HEADER_KEY] = self.api_key
            session.headers.update(headers)
        return session

    def _make_api_call_base(self, http_method, uri, data=None):
        session_method = getattr(self._session, http_method.lower())
        url = self._build_uri(uri)
        if data:
            response = session_method(url, data=data, timeout=15)
        else:
            response = session_method(url, timeout=15)
        return response

    def make_api_call(self, http_method, uri, data=None):
        response = self._make_api_call_base(http_method, uri, data)
        if response.ok:
            try:
                return response.json()
            except ValueError:
                return response.text
        elif response.status_code in range(400, 600):
            self._logger.critical(str(response.headers['Message']).replace("\\", ""))
            sys.exit()
        sys.exit(response.text)

    def _build_uri(self, uri_part):
        uri_parts = []
        uri_part = uri_part.lstrip("/")
        if uri_part.startswith(self._API_BASE_PATH):
            uri_parts.append(uri_part)
        else:
            uri_parts.extend([self._API_BASE_PATH, uri_part])
        return join(*uri_parts)
