# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[by-id] 1'] = {
    'data': {
        'log': {
            'id_': '1',
            'level': 'DEBUG',
            'message': 'A debug message!',
            'time': '2021-01-04T14:32:20'
        }
    }
}
