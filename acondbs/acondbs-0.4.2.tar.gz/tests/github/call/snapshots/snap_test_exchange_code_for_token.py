# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_error 1'] = [
    (
        (
        ),
        {
        }
    ),
    (
        (
            'https://github.com/login/oauth/access_token'
        ,),
        {
            'headers': {
                'Accept': 'application/vnd.github.v3+json, application/json'
            },
            'json': {
                'client_id': 'client_id_0123',
                'client_secret': 'client_secret_0123',
                'code': 'code-xyz',
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost/auth'
            }
        }
    )
]

snapshots['test_success 1'] = [
    (
        (
        ),
        {
        }
    ),
    (
        (
            'https://github.com/login/oauth/access_token'
        ,),
        {
            'headers': {
                'Accept': 'application/vnd.github.v3+json, application/json'
            },
            'json': {
                'client_id': 'client_id_0123',
                'client_secret': 'client_secret_0123',
                'code': 'code-xyz',
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost/auth'
            }
        }
    )
]
