import logging
import requests
from urllib.parse import urlencode

from .utils import url_join

logging.getLogger("nagios").addHandler(logging.NullHandler())


class RestClient:
    DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, url, username, password, timeout=75, verify=False):
        self.url = url
        self.timeout = int(timeout)
        self.verify = bool(verify)
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._create_session(username=self._username, password=self._password)

        if not self.verify:
            requests.packages.urllib3.disable_warnings()

    def _create_session(self, username, password):
        self._session.auth = (username, password)

    def _close_session(self):
        return self._session.close()

    @staticmethod
    def _response_handler(response):
        if not response.text:
            return None

        try:
            return response.json()
        except ValueError:
            logging.debug("Received response with no content")
            return None
        except Exception as e:
            logging.error(e)
            return None

    def raise_for_status(self, response):
        response.raise_for_status()

    def request(
        self,
        method="GET",
        path=None,
        data=None,
        params=None,
        headers=None,
    ):
        url = url_join(url=self.url, path=path)

        if params:
            url += "?" + urlencode(params)

        response = self._session.request(
            method=method,
            url=url,
            headers=headers or self.DEFAULT_HEADERS,
            data=data,
            timeout=self.timeout,
            verify=self.verify,
        )
        response.encoding = "utf-8"

        logging.debug(
            "RestClient: %s %s -> %s %s",
            method,
            path,
            response.status_code,
            response.reason,
        )
        logging.debug("RestClient: Response text -> %s", response.text)

        self.raise_for_status(response)

        return response

    def get(
        self,
        path,
        data=None,
        params=None,
        headers=None,
    ):
        response = self.request(
            method="GET", path=path, params=params, data=data, headers=headers
        )

        if not response.text:
            return None

        return self._response_handler(response)

    def post(
        self,
        path,
        data=None,
        params=None,
        headers=None,
    ):
        response = self.request(
            method="POST", path=path, params=params, data=data, headers=headers
        )

        if not response.text:
            return None

        print(response)

        return self._response_handler(response)

    def put(
        self,
        path,
        data=None,
        params=None,
        headers=None,
    ):
        response = self.request(
            method="POST", path=path, params=params, data=data, headers=headers
        )

        if not response.text:
            return None

        return self._response_handler(response)

    def delete(
        self,
        path,
        data=None,
        params=None,
        headers=None,
    ):
        response = self.request(
            method="POST", path=path, params=params, data=data, headers=headers
        )

        if not response.text:
            return None

        return self._response_handler(response)
