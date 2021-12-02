# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[deleteProductFilePath-error] 1'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'productId': 1001
                    }
                },
                {
                    'node': {
                        'productId': 1012
                    }
                },
                {
                    'node': {
                        'productId': 1012
                    }
                },
                {
                    'node': {
                        'productId': 1013
                    }
                },
                {
                    'node': {
                        'productId': 1070
                    }
                },
                {
                    'node': {
                        'productId': 1120
                    }
                },
                {
                    'node': {
                        'productId': 1130
                    }
                },
                {
                    'node': {
                        'productId': 1150
                    }
                },
                {
                    'node': {
                        'productId': 1002
                    }
                },
                {
                    'node': {
                        'productId': 1002
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[deleteProductFilePath] 1'] = {
    'data': {
        'deleteProductFilePath': {
            'ok': True
        }
    }
}

snapshots['test_schema_success[deleteProductFilePath] 2'] = {
    'data': {
        'product': {
            'name': 'lat20190213',
            'note': '''- This is a dummy test with a lat map
- This should not depend on any beam''',
            'paths': {
                'edges': [
                ]
            },
            'timePosted': '2019-02-13T10:05:23'
        }
    }
}
