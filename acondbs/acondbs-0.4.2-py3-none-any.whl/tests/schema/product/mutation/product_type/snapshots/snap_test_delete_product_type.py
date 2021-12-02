# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error-nonexistent] 1'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'name': 'map',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'name': 'beam',
                        'typeId': '2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_error[error-unempty] 1'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'name': 'map',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'name': 'beam',
                        'typeId': '2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[delete] 1'] = {
    'data': {
        'deleteProductType': {
            'ok': True
        }
    }
}

snapshots['test_schema_success[delete] 2'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'name': 'map',
                        'typeId': '1'
                    }
                }
            ]
        }
    }
}
