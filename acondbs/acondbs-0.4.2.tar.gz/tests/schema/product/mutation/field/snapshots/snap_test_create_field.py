# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[by-enum-int] 1'] = {
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

snapshots['test_schema_error[enum-nonexistent] 1'] = {
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

snapshots['test_schema_success[by-enum-name] 1'] = {
    'data': {
        'createField': {
            'field': {
                'fieldId': '4',
                'name': 'author',
                'type_': 'UNICODE_TEXT'
            },
            'ok': True
        }
    }
}

snapshots['test_schema_success[by-enum-name] 2'] = {
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
                },
                {
                    'node': {
                        'fieldId': '4',
                        'name': 'author',
                        'type_': 'UNICODE_TEXT'
                    }
                }
            ],
            'totalCount': 4
        }
    }
}
