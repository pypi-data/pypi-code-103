# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[query] 1'] = {
    'data': {
        'allProductRelations': {
            'edges': [
                {
                    'node': {
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
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1',
                            'productId': '1'
                        },
                        'relationId': '2',
                        'reverse': {
                            'relationId': '1'
                        },
                        'self_': {
                            'name': 'beam1',
                            'productId': '4'
                        },
                        'type_': {
                            'name': 'parent',
                            'typeId': '1'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2',
                            'productId': '5'
                        },
                        'relationId': '3',
                        'reverse': {
                            'relationId': '4'
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
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1',
                            'productId': '1'
                        },
                        'relationId': '4',
                        'reverse': {
                            'relationId': '3'
                        },
                        'self_': {
                            'name': 'beam2',
                            'productId': '5'
                        },
                        'type_': {
                            'name': 'parent',
                            'typeId': '1'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2',
                            'productId': '5'
                        },
                        'relationId': '5',
                        'reverse': {
                            'relationId': '6'
                        },
                        'self_': {
                            'name': 'beam1',
                            'productId': '4'
                        },
                        'type_': {
                            'name': 'child',
                            'typeId': '2'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1',
                            'productId': '4'
                        },
                        'relationId': '6',
                        'reverse': {
                            'relationId': '5'
                        },
                        'self_': {
                            'name': 'beam2',
                            'productId': '5'
                        },
                        'type_': {
                            'name': 'parent',
                            'typeId': '1'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['test_schema[total-count] 1'] = {
    'data': {
        'allProductRelations': {
            'totalCount': 6
        }
    }
}
