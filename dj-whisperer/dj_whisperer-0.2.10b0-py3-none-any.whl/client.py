import hashlib
import hmac
import json

import requests
from requests.auth import HTTPBasicAuth
from rest_framework.utils.encoders import JSONEncoder

from whisperer.conf import settings


class WebhookClient(object):
    def __init__(self, event_type, payload):
        self.event_type = event_type
        self.payload = payload
        self.headers = {
            'Content-Type': 'application/json',
            'X-Whisperer-Event': self.event_type,
        }

    def sign(self, secret_key, payload):
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            digestmod=hashlib.sha256,
        )
        self.headers['X-Whisperer-Signature'] = 'sha256={}'.format(
            signature.hexdigest()
        )

    def send_payload(
        self,
        target_url,
        payload,
        secret_key=None,
        additional_headers=None,
        auth_config=None,
        *args,
        **kwargs
    ):
        payload = json.dumps(payload, cls=JSONEncoder)
        auth = None
        if secret_key:
            self.sign(secret_key, payload)
        if auth_config:
            auth = self._get_auth(auth_config)
        if additional_headers:
            self.headers.update(additional_headers)
        response = requests.post(
            url=target_url,
            data=payload,
            headers=self.headers,
            timeout=settings.WHISPERER_REQUEST_TIMEOUT,
            auth=auth,
        )
        return response

    def _get_auth(self, auth_config):
        if auth_config.get('auth_type') == 'basic':
            username = auth_config.get('username')
            password = auth_config.get('password')
            return HTTPBasicAuth(username, password)
        if auth_config.get('auth_type') == 'token':
            result = self._get_token(auth_config)
            self._update_header(auth_config, result)

    def _update_header(self, auth_config, result):
        token_key = auth_config.get('token_key', 'key')
        header_format = auth_config.get('header_format', 'Token {}')
        if result.status_code < 400:
            result = result.json()
            token = result.get(token_key)
            self.headers.update(
                {'Authorization': header_format.format(token)})

    def _get_token(self, auth_config):
        username = auth_config.get('username')
        password = auth_config.get('password')
        auth_url = auth_config.get('url')
        username_field = auth_config.get('username_field', 'username')
        password_field = auth_config.get('password_field', 'password')

        result = requests.post(url=auth_url,
                               data={username_field: username,
                                     password_field: password})
        return result
