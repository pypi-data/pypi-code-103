# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[type_id-nonexistent] 1'] = {
    'data': {
        'productRelation': None
    }
}

snapshots['test_schema[type_id] 1'] = {
    'data': {
        'productRelation': {
            'other': {
                'name': 'beam1',
                'productId': '4'
            },
            'relationId': '1',
            'reverse': {
                'relationId': '2'
            },
            'self_': {
                'name': 'map1',
                'productId': '1'
            },
            'type_': {
                'name': 'child',
                'typeId': '2'
            }
        }
    }
}
