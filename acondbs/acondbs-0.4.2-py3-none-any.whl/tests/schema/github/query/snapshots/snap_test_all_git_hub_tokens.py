# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[filter] 1'] = {
    'data': {
        'allGitHubTokens': {
            'edges': [
                {
                    'node': {
                        'scope': 'read:org',
                        'timeCreated': '2021-01-04T14:32:20',
                        'tokenId': '1',
                        'tokenMasked': 'XXXXXXXXXXXXXXX',
                        'user': {
                            'login': 'user1'
                        }
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['test_schema[simple] 1'] = {
    'data': {
        'allGitHubTokens': {
            'edges': [
                {
                    'node': {
                        'scope': 'read:org',
                        'timeCreated': '2021-01-04T14:32:20',
                        'tokenId': '1',
                        'tokenMasked': 'XXXXXXXXXXXXXXX',
                        'user': {
                            'login': 'user1'
                        }
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'timeCreated': '2021-01-04T14:32:20',
                        'tokenId': '2',
                        'tokenMasked': 'XXXXXXXXXXXXXXX',
                        'user': {
                            'login': 'user1'
                        }
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'timeCreated': '2021-01-04T14:32:20',
                        'tokenId': '3',
                        'tokenMasked': 'XXXXXXXXXXXXXXX',
                        'user': {
                            'login': 'user2'
                        }
                    }
                },
                {
                    'node': {
                        'scope': '',
                        'timeCreated': '2021-01-04T14:32:20',
                        'tokenId': '4',
                        'tokenMasked': 'XXXXXXXXXXXXXXX',
                        'user': {
                            'login': 'user3'
                        }
                    }
                }
            ],
            'totalCount': 4
        }
    }
}
