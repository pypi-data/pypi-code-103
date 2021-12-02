# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[one] 1'] = {
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
                },
                {
                    'node': {
                        'id_': '2',
                        'level': 'ERROR',
                        'message': 'An error message!',
                        'time': '2021-01-04T14:32:20'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}
