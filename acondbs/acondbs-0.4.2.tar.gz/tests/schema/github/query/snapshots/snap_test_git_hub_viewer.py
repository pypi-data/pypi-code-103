# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_success[one] 1'] = {
    'data': {
        'gitHubViewer': {
            'avatarUrl': 'avatar.com/user1',
            'login': 'user1',
            'name': 'User One'
        }
    }
}
