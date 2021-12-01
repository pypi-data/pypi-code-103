import urllib.parse
from typing import List

import requests
from requests import Response

from .conversion import serialize_resolve_request, deserialize_pseudonym_match
from .model import ResolveRequest, PseudonymMatch
from ..restutil import append_auth_header, ApiError, prepare_url_for_relative_urljoin


def _try_raise_error(r: Response):
    """
    Tries to read an error message from a HTTP response to raise it as an instance of ``ApiError``.
    """
    try:
        data = r.json()
        error = data["error"]

        raise ApiError(f"Couldn't submit bit strings: {error}", r.status_code)
    except ValueError:
        raise ApiError(f"Couldn't submit bit strings: {r.text}", r.status_code)
    except KeyError:
        raise ApiError(f"Couldn't submit bit strings: {r.text}", r.status_code)


def submit_pseudonyms(base_url: str, secret: str, request: ResolveRequest):
    """
    Submits pseudonyms to a pseudonym resolver service.

    :param base_url: URL at which the pseudonym resolver service is hosted
    :param secret: Session secret obtained at the broker
    :param request: Request to send to pseudonym resolver
    """
    r = requests.post(base_url, json=serialize_resolve_request(request),
                      headers=append_auth_header(secret))

    if r.status_code >= 400:
        _try_raise_error(r)


def get_results(base_url: str, secret: str) -> List[PseudonymMatch]:
    """
    Retrieves results from a pseudonym resolver service.

    :param base_url: URL at which the pseudonym resolver service is hosted
    :param secret: Session secret obtained at the broker
    """
    r = requests.get(base_url, headers=append_auth_header(secret))

    if r.status_code >= 400:
        _try_raise_error(r)

    return [
        deserialize_pseudonym_match(match) for match in r.json()["matches"]
    ]


def get_attributes(base_url: str) -> List[str]:
    """
    Retrieves a list of valid attribute names that may be sent along with a submission request.

    :param base_url: URL at which the pseudonym resolver service is hosted
    :return: List of supported attributes
    """
    base_url = prepare_url_for_relative_urljoin(base_url)
    url = urllib.parse.urljoin(base_url, "attributes")

    r = requests.get(url)

    if r.status_code >= 400:
        _try_raise_error(r)

    return r.json()


class ResolverClient:

    def __init__(self, base_url: str):
        self.__base_url = base_url

    def submit_pseudonyms(self, secret: str, request: ResolveRequest):
        """
        Submits pseudonyms to a pseudonym resolver service.

        :param secret: Session secret obtained at the broker
        :param request: Request to send to pseudonym resolver
        """
        return submit_pseudonyms(self.__base_url, secret, request)

    def get_results(self, secret: str) -> List[PseudonymMatch]:
        """
        Retrieves results from a pseudonym resolver service.

        :param secret: Session secret obtained at the broker
        """
        return get_results(self.__base_url, secret)

    def get_attributes(self) -> List[str]:
        """
        Retrieves a list of valid attribute names that may be sent along with a submission request.

        :return: List of supported attributes
        """
        return get_attributes(self.__base_url)
