# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[one] 1'] = {
    'data': {
        'allFields': {
            'edges': [
                {
                    'node': {
                        'fieldId': '1',
                        'name': 'contact',
                        'type_': 'UNICODE_TEXT'
                    }
                },
                {
                    'node': {
                        'fieldId': '2',
                        'name': 'produced_by',
                        'type_': 'UNICODE_TEXT'
                    }
                },
                {
                    'node': {
                        'fieldId': '3',
                        'name': 'date_produced',
                        'type_': 'DATE'
                    }
                }
            ],
            'totalCount': 3
        }
    }
}
