# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[deep] 1'] = {
    'data': {
        'product': {
            'attributesBoolean': {
                'edges': [
                ]
            },
            'attributesDate': {
                'edges': [
                    {
                        'node': {
                            'field': {
                                'name': 'date_produced',
                                'type_': 'DATE'
                            },
                            'typeFieldAssociation': {
                                'field': {
                                    'name': 'date_produced',
                                    'type_': 'DATE'
                                }
                            },
                            'value': '2020-02-01'
                        }
                    }
                ]
            },
            'attributesDateTime': {
                'edges': [
                ]
            },
            'attributesFloat': {
                'edges': [
                ]
            },
            'attributesInteger': {
                'edges': [
                ]
            },
            'attributesTime': {
                'edges': [
                ]
            },
            'attributesUnicodeText': {
                'edges': [
                    {
                        'node': {
                            'field': {
                                'name': 'contact',
                                'type_': 'UNICODE_TEXT'
                            },
                            'typeFieldAssociation': {
                                'field': {
                                    'name': 'contact',
                                    'type_': 'UNICODE_TEXT'
                                }
                            },
                            'value': None
                        }
                    },
                    {
                        'node': {
                            'field': {
                                'name': 'produced_by',
                                'type_': 'UNICODE_TEXT'
                            },
                            'typeFieldAssociation': {
                                'field': {
                                    'name': 'produced_by',
                                    'type_': 'UNICODE_TEXT'
                                }
                            },
                            'value': None
                        }
                    }
                ]
            },
            'name': 'map1',
            'note': None,
            'paths': {
                'edges': [
                    {
                        'node': {
                            'note': None,
                            'path': 'site2:/another/way/map1',
                            'pathId': '1'
                        }
                    },
                    {
                        'node': {
                            'note': 'sample comment',
                            'path': 'site1:/path/to/map1',
                            'pathId': '8'
                        }
                    }
                ]
            },
            'postingGitHubUser': None,
            'productId': '1',
            'relations': {
                'edges': [
                    {
                        'node': {
                            'other': {
                                'name': 'beam1',
                                'productId': '4',
                                'typeId': 2,
                                'type_': {
                                    'name': 'beam',
                                    'typeId': '2'
                                }
                            },
                            'otherProductId': 4,
                            'relationId': '1',
                            'reverse': {
                                'relationId': '2',
                                'typeId': 1,
                                'type_': {
                                    'name': 'parent',
                                    'typeId': '1'
                                }
                            },
                            'reverseRelationId': 2,
                            'typeId': 2,
                            'type_': {
                                'name': 'child',
                                'typeId': '2'
                            }
                        }
                    },
                    {
                        'node': {
                            'other': {
                                'name': 'beam2',
                                'productId': '5',
                                'typeId': 2,
                                'type_': {
                                    'name': 'beam',
                                    'typeId': '2'
                                }
                            },
                            'otherProductId': 5,
                            'relationId': '3',
                            'reverse': {
                                'relationId': '4',
                                'typeId': 1,
                                'type_': {
                                    'name': 'parent',
                                    'typeId': '1'
                                }
                            },
                            'reverseRelationId': 4,
                            'typeId': 2,
                            'type_': {
                                'name': 'child',
                                'typeId': '2'
                            }
                        }
                    }
                ]
            },
            'timePosted': '2021-01-04T14:32:20',
            'timeUpdated': None,
            'typeId': 1,
            'type_': {
                'name': 'map',
                'typeId': '1'
            },
            'updatingGitHubUser': None
        }
    }
}

snapshots['test_schema[product_id-name-nonexistent] 1'] = {
    'data': {
        'product': None
    }
}

snapshots['test_schema[product_id-name] 1'] = {
    'data': {
        'product': {
            'name': 'map1',
            'productId': '1',
            'typeId': 1
        }
    }
}

snapshots['test_schema[product_id-nonexistent] 1'] = {
    'data': {
        'product': None
    }
}

snapshots['test_schema[type_id-name] 1'] = {
    'data': {
        'product': {
            'name': 'map1',
            'productId': '1',
            'typeId': 1
        }
    }
}
