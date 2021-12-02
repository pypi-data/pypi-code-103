# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[updateProductFilePath-immutableField] 1'] = {
    'data': {
        'product': {
            'paths': {
                'edges': [
                    {
                        'node': {
                            'note': '',
                            'path': 'nersc:/go/to/my/maps',
                            'product': {
                                'productId': '1001'
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_schema_success[updateProductFilePath] 1'] = {
    'data': {
        'updateProductFilePath': {
            'productFilePath': {
                'path': 'nersc:/go/to/my/new_product_v2'
            }
        }
    }
}

snapshots['test_schema_success[updateProductFilePath] 2'] = {
    'data': {
        'product': {
            'name': 'lat20190213',
            'note': '''- This is a dummy test with a lat map
- This should not depend on any beam''',
            'paths': {
                'edges': [
                    {
                        'node': {
                            'note': '- Note 1 updated',
                            'path': 'nersc:/go/to/my/new_product_v2',
                            'product': {
                                'productId': '1001'
                            }
                        }
                    }
                ]
            },
            'timePosted': '2019-02-13T10:05:23'
        }
    }
}
