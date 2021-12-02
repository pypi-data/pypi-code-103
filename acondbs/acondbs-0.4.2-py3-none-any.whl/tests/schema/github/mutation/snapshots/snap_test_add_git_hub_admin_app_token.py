# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[one] 1'] = {
    'data': {
        'allGitHubTokens': {
            'edges': [
                {
                    'node': {
                        'scope': 'read:org',
                        'tokenId': '1',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '2',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '3',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '4',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                }
            ],
            'totalCount': 4
        }
    }
}

snapshots['test_schema_error[one] 2'] = [
    (
        (
            'code_01234'
        ,),
        {
        }
    )
]

snapshots['test_schema_success[one] 1'] = {
    'data': {
        'addGitHubAdminAppToken': {
            'ok': True
        }
    }
}

snapshots['test_schema_success[one] 2'] = {
    'data': {
        'allGitHubTokens': {
            'edges': [
                {
                    'node': {
                        'scope': 'read:org',
                        'tokenId': '1',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '2',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '3',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'tokenId': '4',
                        'tokenMasked': 'XXXXXXXXXXXXXXX'
                    }
                }
            ],
            'totalCount': 4
        }
    }
}

snapshots['test_schema_success[one] 3'] = [
    (
        (
            'code_01234'
        ,),
        {
        }
    )
]
