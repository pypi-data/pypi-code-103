import urllib.parse
from typing import Dict


def prepare_url_for_relative_urljoin(url: str) -> str:
    """
    Strips all URL components except for the scheme, host and path.
    If the path doesn't have a trailing slash, it is then added.

    :param url: URL to modify
    :return: Modified URL
    """
    scheme, netloc, path, _, _, _, = urllib.parse.urlparse(url)

    # remove trailing slash from path if it exists
    if not path.endswith("/"):
        path = path + "/"

    return urllib.parse.urlunparse((scheme, netloc, path, "", "", ""))


def append_auth_header(token: str, headers: Dict[str, str] = None):
    """
    Appends a Bearer authorization header to the provided dictionary of headers.

    :param headers: Dictionary of headers
    :param token: Authorization token
    :return: Header dictionary with additional authorization header
    """
    if headers is None:
        headers = {}

    headers["Authorization"] = f"Bearer {token}"
    return headers


class ApiError(ConnectionError):

    def __init__(self, message: str, code: int):
        """
        Constructs a generic error message representing that the returned status code of an API did not match
        the expected status code.

        :param message: Error message
        :param code: Status code returned by the API
        """
        super().__init__(self, message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.message}: service returned status code {self.code}"
