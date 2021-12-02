# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[dojocat] 1'] = {
    'data': {
        'isAdmin': False
    }
}

snapshots['test_schema[octocat] 1'] = {
    'data': {
        'isAdmin': True
    }
}
