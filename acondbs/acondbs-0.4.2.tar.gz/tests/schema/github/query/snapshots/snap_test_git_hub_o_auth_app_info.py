# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[query] 1'] = {
    'data': {
        'gitHubOAuthAppInfo': {
            'authorizeUrl': 'https://github.com/login/oauth/authorize',
            'clientId': 'client_id_0123456789',
            'redirectUri': 'http://localhost:8080/signin'
        }
    }
}
