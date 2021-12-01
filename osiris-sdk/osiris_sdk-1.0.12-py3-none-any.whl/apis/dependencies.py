"""
Contains common functionalities for Egress and Ingress API's
"""
import json
import logging
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any

from requests import Response


logger = logging.getLogger(__name__)


def handle_retrieve_state_response(response: Response) -> Any:
    """
     Checks status codes and converts JSON string to Python objects. Returns empty list if no result was found.
    """
    if response.status_code == HTTPStatus.NOT_FOUND:
        return {}

    check_status_code(response)

    try:
        return json.loads(response.content)
    except JSONDecodeError:
        message = 'File is not correctly JSON formatted.'
        raise ValueError(message) from JSONDecodeError


def handle_download_response(response: Response) -> Any:
    """
     Checks status codes and converts JSON string to Python objects. Returns empty list if no result was found.
    """

    check_status_code(response)

    if response.status_code == HTTPStatus.NO_CONTENT:
        return []

    try:
        return json.loads(response.content)
    except JSONDecodeError:
        message = 'File is not correctly JSON formatted.'
        raise ValueError(message) from JSONDecodeError


def handle_parquet_response(response: Response) -> Any:
    """
     Checks status codes and converts JSON string to Python objects. Returns empty list if no result was found.
    """

    check_status_code(response)

    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    return response.content


def __get_detail(response: str):
    try:
        detail = json.loads(response)
        if isinstance(detail, dict) and 'detail' in detail:
            return detail['detail']
        return response
    except JSONDecodeError:
        return response


def check_status_code(response: Response):
    """
    Converts HTTP errors to Python Exceptions
    """
    if response.status_code == HTTPStatus.BAD_GATEWAY:
        # The response in response.text gives only 502 Bad Gateway in HTML
        # This is often caused by processing too much data in Egress-API
        detail = '(502 Bad Gateway) Often caused by too large dataset request - try to limit date range requested'
        raise Exception(detail)

    if response.status_code == HTTPStatus.NOT_FOUND:
        detail = __get_detail(response.text)
        raise FileNotFoundError(detail)

    if response.status_code == HTTPStatus.BAD_REQUEST:
        detail = __get_detail(response.text)
        raise ValueError(detail)

    if response.status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED):
        detail = __get_detail(response.text)
        raise PermissionError(detail)

    if response.status_code in (HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.UNPROCESSABLE_ENTITY):
        detail = __get_detail(response.text)
        raise Exception(detail)


def check_upload_status_code(response: Response):
    """
    Converts HTTP errors to Python Exceptions
    """
    check_status_code(response)
    if response.status_code != HTTPStatus.CREATED:
        detail = __get_detail(response.text)
        raise Exception(detail)
