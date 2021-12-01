#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import os
from flask import current_app, g
from requests.adapters import HTTPAdapter
from requests_toolbelt.adapters import host_header_ssl

from ..providers.oidc_provider import JWTEncoded


class BaseAdapter(HTTPAdapter):

    def __init__(self, *args, **kwargs):
        # Let the interface know this is an internal request
        self.user_agent = '{} / {}'.format(
            os.environ.get('CI_PROJECT_NAME', 'consumption'),
            os.environ.get('CI_ENVIRONMENT_SLUG', 'unknown'),
        )

        super().__init__(*args, **kwargs)

    def add_headers(self, request, **kwargs):
        request.headers['User-Agent'] = self.user_agent
        super().add_headers(request, **kwargs)


class DlcAdapter(BaseAdapter):
    def add_headers(self, request, **kwargs):
        request.headers['Authorization'] = 'Bearer {}'.format(
            current_app.injector.get(JWTEncoded)
        )

        request.headers['X-Request-ID'] = getattr(
            g, 'request_id', 'missing'
        )

        super().add_headers(request, **kwargs)


class DLIAdapter(host_header_ssl.HostHeaderSSLAdapter):

    def __init__(self, session, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    def add_headers(self, request, **kwargs):
        # Generate request_id on the SDK side for use in Consumption log
        # messages. This is useful for debugging what seems like a success
        # (no exception) but is not what the user wanted e.g. not the data
        # they expected.

        super().add_headers(request, **kwargs)


class DLIBearerAuthAdapter(DLIAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)
        if self.session.auth_key and 'Authorization' not in request.headers:
            request.headers['Authorization'] = f'Bearer {self.session.auth_key}'


class DLISirenAdapter(DLIAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)
        request.headers['Content-Type'] = "application/vnd.siren+json"


class DLICookieAuthAdapter(DLIAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)
        # Accounts V1 authentication is broken, in that it only accepts
        # a cookie rather than an API key.
        request.headers['Cookie'] = f'oidc_id_token={self.session.auth_key}'


class DLIAccountsV1Adapter(DLISirenAdapter, DLICookieAuthAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)


class DLIInterfaceV1Adapter(DLISirenAdapter, DLIBearerAuthAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)


class DLISamAdapter(DLIAdapter):
    def add_headers(self, request, **kwargs):
        super().add_headers(request, **kwargs)
        request.headers['Content-Type'] = "application/x-www-form-urlencoded"