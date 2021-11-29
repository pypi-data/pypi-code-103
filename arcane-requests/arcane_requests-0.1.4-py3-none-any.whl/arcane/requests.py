from typing import Optional, Dict, Callable
from typing_extensions import Literal

import json
import backoff
import requests

from arcane.firebase import generate_token as generate_firebase_token, initialize_app
from google.oauth2 import service_account, id_token
import google.auth.transport.requests


def _generate_id_token(credentials_path: str,
                       url: str):
    request = google.auth.transport.requests.Request()
    creds = service_account.IDTokenCredentials.from_service_account_file(
        credentials_path,
        target_audience=url)
    creds.refresh(request)
    token = creds.token
    id_token.verify_token(token, request)
    return token


def request_service(method: str,
                    url: str,
                    firebase_api_key: str = None,
                    claims: object = None,
                    uid: str = None,
                    token_type: Literal['firebase', 'id_token'] = 'firebase',
                    headers: Optional[Dict] = None,
                    retry_decorator: Callable[[requests.request], requests.request] = lambda f: f,
                    auth_enabled: bool = True,
                    credentials_path: str = None,
                    **kwargs) -> requests.Response:
    """ call service while adding a google generated token to it """

    if headers is None:
        headers = {"content-type": "application/json"}
    if auth_enabled:
        if token_type == 'firebase':
            if firebase_api_key is None:
                raise ValueError('Firebase API Key must be set when token_type is firebase')
            if uid is None:
                uid = 'adscale@arcane.run'
            try:
                token = generate_firebase_token(firebase_api_key, claims, uid)
            except ValueError as err:
                if str(err).startswith('The default Firebase app does not exist.') and\
                        credentials_path is not None:
                    initialize_app(credentials_path)
                    token = generate_firebase_token(firebase_api_key, claims, uid)
                else:
                    raise err
        elif token_type == 'id_token':
            if credentials_path is None:
                raise ValueError('Credentials path must be set when token_type is id_token')
            token = _generate_id_token(credentials_path, url)
        else:
            raise ValueError(f'Token type {token_type} is not supported')

        headers.update(Authorization=f'bearer {token}')

    @retry_decorator
    def request_with_retries():
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    return request_with_retries()


def call_get_route(url: str, firebase_api_key: str, claims: object, auth_enabled: bool, credentials_path: str = None, uid: str = None):
    response = request_service('GET',
                               url,
                               firebase_api_key,
                               claims=claims,
                               uid=uid,
                               auth_enabled=auth_enabled,
                               retry_decorator=backoff.on_exception(
                                    backoff.expo,
                                    (ConnectionError, requests.HTTPError, requests.Timeout),
                                    3
                                ),
                               credentials_path=credentials_path)
    response.raise_for_status()
    return json.loads(response.content.decode("utf8"))
