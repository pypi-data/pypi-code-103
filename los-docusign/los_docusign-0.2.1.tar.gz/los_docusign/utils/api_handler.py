"""Module to define base handler for external API calls"""

import logging

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ProxyError,
    ReadTimeout,
    SSLError,
    Timeout,
    TooManyRedirects,
)

LOGGER = logging.getLogger("root")


class ApiHandler:
    """Base class for calling any external APIs"""

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.__api_key = api_key

        self.timeout = 15  # seconds
        self.extra_headers = {}
        self.connection_exceptions = (
            ConnectionError,
            ProxyError,
            ReadTimeout,
            SSLError,
            Timeout,
            TooManyRedirects,
        )

    def get_headers(self, **kwargs):
        """Builds and return headers for each request"""
        kwargs.setdefault("Content-Type", "application/json")
        kwargs.setdefault("Accept", "application/json")
        kwargs.setdefault("Authorization", self.__api_key)

        kwargs.update(self.extra_headers)
        return kwargs

    def send_request(self, method, params=None, payload=None, extra_headers=None):
        """Send API request for the given URL with the specified method, params and payload"""
        headers = self.get_headers()

        if extra_headers is not None:
            headers.update(extra_headers)

        try:
            response = requests.request(
                method,
                self.url,
                timeout=self.timeout,
                headers=headers,
                params=params,
                # TODO: Try changing to json=payload
                data=payload,
            )

            response.raise_for_status()
            return response
        except self.connection_exceptions as excp:
            # TODO: Handle connection errors and to raise 500
            LOGGER.error(f"Exception while connecting to DocuSign : {excp}")
            raise
        except HTTPError as excp:
            # TODO: Handle API errors
            LOGGER.error(f"Exception while connecting to DocuSign : {excp}")
            raise
