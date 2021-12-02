# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_success[one] 1'] = {
    'data': {
        'deleteLog': {
            'ok': True
        }
    }
}

snapshots['test_schema_success[one] 2'] = {
    'data': {
        'allLogs': {
            'edges': [
                {
                    'node': {
                        'id_': '1',
                        'level': 'DEBUG',
                        'message': 'A debug message!',
                        'time': '2021-01-04T14:32:20'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
