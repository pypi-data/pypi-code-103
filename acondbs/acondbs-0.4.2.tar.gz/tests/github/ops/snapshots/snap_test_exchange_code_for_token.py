# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_call 1'] = [
    (
        (
            'kp5b8653'
        ,),
        {
            'client_id': 'client_id_0123456789',
            'client_secret': 'client_secret_abcdefghijklmnupqrstuvwxyz',
            'redirect_uri': 'http://localhost:8080/signin',
            'token_url': 'https://github.com/login/oauth/access_token'
        }
    )
]
