# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_simple 1'] = [
    (
        (
        ),
        {
        }
    ),
    (
        (
            'https://api.github.com/graphql'
        ,),
        {
            'headers': {
                'Authorization': 'token token-xxx'
            },
            'json': {
                'query': '{ viewer { login name avatarUrl } }'
            }
        }
    )
]

snapshots['test_variables 1'] = [
    (
        (
        ),
        {
        }
    ),
    (
        (
            'https://api.github.com/graphql'
        ,),
        {
            'headers': {
                'Authorization': 'token token-xxx'
            },
            'json': {
                'query': '''
      query Organization($org_login: String!) {
        organization(login: $org_login) {
          login
          avatarUrl
        }
      }
    ''',
                'variables': {
                    'org_login': 'urban-octo-disco'
                }
            }
        }
    )
]
