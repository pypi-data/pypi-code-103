# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[createProductFilePath-noSuchField] 1'] = {
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

snapshots['test_schema_success[createProductFilePath] 1'] = {
    'data': {
        'createProductFilePath': {
            'productFilePath': {
                'path': 'nersc:/go/to/my/new_product_v1'
            }
        }
    }
}

snapshots['test_schema_success[createProductFilePath] 2'] = {
    'data': {
        'product': {
            'name': '20180101',
            'note': '- test entry',
            'paths': {
                'edges': [
                    {
                        'node': {
                            'note': '- Note 1',
                            'path': 'nersc:/go/to/my/new_product_v1',
                            'product': {
                                'productId': '1010'
                            }
                        }
                    }
                ]
            },
            'timePosted': '2018-01-01T15:32:10'
        }
    }
}
