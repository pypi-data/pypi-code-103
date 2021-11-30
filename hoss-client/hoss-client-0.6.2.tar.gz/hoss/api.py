from typing import Optional
from urllib.parse import urlparse

import requests
from packaging import version

from hoss.version import __version__
from hoss.error import *
from hoss.auth import AuthService


# Currently must be a 0.2.1 or later server
MIN_SUPPORTED_SERVER_VERSION = "0.2.1"
MAX_SUPPORTED_SERVER_VERSION = "0.2.99999999"


class CoreAPI(object):
    def __init__(self, server_url: str, auth_instance: Optional[AuthService] = None):
        """A root class to interact with the Hoss core API
        
        Args:
            server_url: root URL to the server, including the protocol
            auth_instance: an optional AuthService instance that will be used instead of using the server_url to
                           instantiate one. This is useful if working with 2 linked servers without having to switch
                           HOS_PAT env vars.
        """
        parts = urlparse(server_url)
        self.host = parts.netloc
        self.base_url = f"{parts.scheme}://{parts.netloc}"

        self._verify_server_version()

        if auth_instance:
            self.auth = auth_instance
        else:
            # Discover the auth endpoint you should be using by calling the core service discovery endpoint
            response = requests.get(f"{self.base_url}/core/v1/discover")
            if response.status_code != 200:
                raise HossException(f"Failed to reach discover endpoint for server '{self.base_url}' when trying "
                                    f"to initialize auth")
            data = response.json()
            self.auth = AuthService(data['auth_service'])

    def _request(self, method: str, path, json=None) -> Optional[dict]:
        """Method to make a request to the API

        Args:
            method: HTTP method
            path: relative path in the API (i.e. after <host>/core/v1). Includes the leading slash
            json: dictionary to encode as json in the POST body

        Returns:
            dictionary of the json formatted response, if present
        """
        kwargs = {
            "headers": {
                "Access-Control-Request-Method": method,
                "Origin": self.base_url,
                **self.auth.headers(),
            },
        }
        if json:
            kwargs["json"] = json

        resp = requests.request(method, f"{self.base_url}/core/v1{path}", **kwargs)
        if resp.ok:
            if resp.text == "":
                return None
            else:
                return resp.json()
        if resp.status_code == 401:
            raise NotAuthorizedException()
        if resp.status_code == 404:
            raise NotFoundException()
        if resp.status_code == 403:
            raise AlreadyExistsException()
        
        try:
            error = resp.json().get("error")

            if error == "Resource not found":
                raise NotFoundException()
            elif error == "Resource already exists":
                raise AlreadyExistsException()
            else:
                raise HossException(error)
        except HossException:
            raise  # don't modify the exceptions just raised
        except:
            raise HossException(f"{resp.status_code} {resp.reason}: {resp.text}")

    def _sync_user_groups(self) -> None:
        """Helper method to synchronize a user's groups. Useful if group membership changed and you need to
        update your groups in the JWT"""
        self._request("PUT", "/user/sync")

    def _verify_server_version(self) -> None:
        """

        Returns:

        """
        kwargs = {
            "headers": {
                "Access-Control-Request-Method": "GET",
                "Origin": self.base_url
            },
        }
        response = requests.request("GET", f"{self.base_url}/core/v1/discover", **kwargs)
        if response.status_code != 200:
            raise HossException(f"Failed to fetch server version. Status Code: {response.status_code}")

        data = response.json()
        server_version = version.parse(data['version'])

        if server_version < version.parse(MIN_SUPPORTED_SERVER_VERSION):
            raise HossException(f"The current client version ({__version__}) is not compatible with this server."
                               f" (Server version: {data['version']}, Minimum supported server version:"
                               f" {MIN_SUPPORTED_SERVER_VERSION}. Downgrade the client and try again.")

        if server_version > version.parse(MAX_SUPPORTED_SERVER_VERSION):
            raise HossException(f"The current client version ({__version__}) is not compatible with this server."
                               f" (Server version: {data['version']}, Maximum supported server version:"
                               f" {MAX_SUPPORTED_SERVER_VERSION}. Upgrade the client and try again.")
