# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[empty-input] 1'] = {
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

snapshots['test_schema_error[non-existent-field] 1'] = {
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

snapshots['test_schema_success[one] 1'] = {
    'data': {
        'updateField': {
            'field': {
                'fieldId': '1',
                'name': 'author',
                'type_': 'UNICODE_TEXT'
            },
            'ok': True
        }
    }
}

snapshots['test_schema_success[one] 2'] = {
    'data': {
        'allFields': {
            'edges': [
                {
                    'node': {
                        'fieldId': '1',
                        'name': 'author',
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
