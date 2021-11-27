# pylint: disable=super-with-arguments
import time

import requests

from rapconector.utils import parse_or_raise


class Session(requests.Session):
    '''
    Wrapper for ``requests.Session``. Implements just the methods we use in
    the client and adds a pre-request hook to ensure we are always authenticated
    before hitting the API endpoints.
    '''
    def __init__(self, *args, **kwargs):
        # Take a reference to the client (needed for base_url, email, password)
        self._rapconector_client = kwargs['_rapconector_client']
        del kwargs['_rapconector_client']

        # Fields for the session authentication data.
        self._jwt = None
        self._jwt_refresh = None
        self._jwt_valid_until = None

        # Default token duration (15 minutes).
        self._default_jwt_timeout = 1000 * 60 * 15

        super(Session, self).__init__(*args, **kwargs)

    def _authenticate(self):
        '''POSTs to the authentication route and saves all the relevant data.'''
        json = parse_or_raise(
            super(Session,
                  self).post(self._rapconector_client.base_url + '/users/auth',
                             json={
                                 'email': self._rapconector_client.email,
                                 'password': self._rapconector_client.password
                             }))

        self._jwt = json['accessToken']
        self._jwt_refresh = json.get('refreshToken')
        self.headers.update({'Authorization': 'Bearer {}'.format(self._jwt)})

        # Generate and save timestamp for when we need to request the token
        # again before another request.
        self._jwt_valid_until = time.time() + self._default_jwt_timeout

    def _ensure_authentication(self):
        '''Tests if token timeout has been exceeded, re-authenticates if so.'''
        if not self._jwt_valid_until or time.time() >= self._jwt_valid_until:
            self._authenticate()

    def get(self, *args, **kwargs):
        self._ensure_authentication()
        return super(Session, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._ensure_authentication()
        return super(Session, self).post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._ensure_authentication()
        return super(Session, self).delete(*args, **kwargs)
