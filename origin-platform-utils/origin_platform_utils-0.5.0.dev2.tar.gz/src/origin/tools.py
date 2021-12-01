from typing import Dict, Any
from urllib.parse import urlencode
import urllib.parse as urlparse


def append_query_parameters(url: str, query_extra: Dict[str, Any]) -> str:
    """
    Provided an URL, this function adds (or overwrites) one or more
    query parameters, and returns the updated URL.

    :param url: The URL to add query parameters to
    :param query_extra: The query parameters to add
    :return: The URL with added query parameters
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(query_extra)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)
