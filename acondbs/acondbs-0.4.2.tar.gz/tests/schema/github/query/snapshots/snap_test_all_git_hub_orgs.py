# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[one] 1'] = {
    'data': {
        'allGitHubOrgs': {
            'edges': [
                {
                    'node': {
                        'login': 'org1',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'member': {
                                            'login': 'user1'
                                        }
                                    }
                                }
                            ],
                            'totalCount': 1
                        }
                    }
                },
                {
                    'node': {
                        'login': 'org2',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'member': {
                                            'login': 'user1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'member': {
                                            'login': 'user2'
                                        }
                                    }
                                }
                            ],
                            'totalCount': 2
                        }
                    }
                },
                {
                    'node': {
                        'login': 'org3',
                        'memberships': {
                            'edges': [
                            ],
                            'totalCount': 0
                        }
                    }
                }
            ],
            'totalCount': 3
        }
    }
}
