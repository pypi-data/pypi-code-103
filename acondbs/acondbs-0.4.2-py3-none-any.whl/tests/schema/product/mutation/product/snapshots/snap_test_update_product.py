# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error-constraint] 1'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[delete-paths] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 1,
                'type_': {
                    'name': 'map',
                    'typeId': '1'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[delete-paths] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[delete-relations] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                                'value': '2020-03-04'
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
                'name': 'beam2',
                'note': None,
                'paths': {
                    'edges': [
                        {
                            'node': {
                                'note': None,
                                'path': 'site1:/path/to/beam2',
                                'pathId': '8'
                            }
                        }
                    ]
                },
                'postingGitHubUser': None,
                'productId': '5',
                'relations': {
                    'edges': [
                    ]
                },
                'timePosted': '2021-01-04T14:32:20',
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 2,
                'type_': {
                    'name': 'beam',
                    'typeId': '2'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[delete-relations] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[update-name] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                'name': 'new-name',
                'note': None,
                'paths': {
                    'edges': [
                        {
                            'node': {
                                'note': None,
                                'path': 'site1:/path/to/map1',
                                'pathId': '1'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': 'site2:/another/way/map1',
                                'pathId': '2'
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
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 1,
                'type_': {
                    'name': 'map',
                    'typeId': '1'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[update-name] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'new-name'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'new-name'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'new-name'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'new-name'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'new-name'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[update-paths] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                                'path': 'site1:/path/to/map1',
                                'pathId': '1'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': 'site2:/updated/way/map1',
                                'pathId': '9'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': 'site4:/additional/map1',
                                'pathId': '10'
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
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 1,
                'type_': {
                    'name': 'map',
                    'typeId': '1'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[update-paths] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/updated/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site4:/additional/map1'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[update-relations] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                                'value': '2020-03-04'
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
                'name': 'beam2',
                'note': None,
                'paths': {
                    'edges': [
                        {
                            'node': {
                                'note': None,
                                'path': 'site1:/path/to/beam2',
                                'pathId': '8'
                            }
                        }
                    ]
                },
                'postingGitHubUser': None,
                'productId': '5',
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
                                'relationId': '6',
                                'reverse': {
                                    'relationId': '5',
                                    'typeId': 2,
                                    'type_': {
                                        'name': 'child',
                                        'typeId': '2'
                                    }
                                },
                                'reverseRelationId': 5,
                                'typeId': 1,
                                'type_': {
                                    'name': 'parent',
                                    'typeId': '1'
                                }
                            }
                        },
                        {
                            'node': {
                                'other': {
                                    'name': 'map2',
                                    'productId': '2',
                                    'typeId': 1,
                                    'type_': {
                                        'name': 'map',
                                        'typeId': '1'
                                    }
                                },
                                'otherProductId': 2,
                                'relationId': '8',
                                'reverse': {
                                    'relationId': '7',
                                    'typeId': 2,
                                    'type_': {
                                        'name': 'child',
                                        'typeId': '2'
                                    }
                                },
                                'reverseRelationId': 7,
                                'typeId': 1,
                                'type_': {
                                    'name': 'parent',
                                    'typeId': '1'
                                }
                            }
                        }
                    ]
                },
                'timePosted': '2021-01-04T14:32:20',
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 2,
                'type_': {
                    'name': 'beam',
                    'typeId': '2'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[update-relations] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'map2'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map2'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[update] 1'] = {
    'data': {
        'updateProduct': {
            'ok': True,
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
                                'value': 'new-contact'
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
                'note': '- updated note 123',
                'paths': {
                    'edges': [
                        {
                            'node': {
                                'note': None,
                                'path': 'site1:/path/to/map1',
                                'pathId': '1'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': 'site2:/another/way/map1',
                                'pathId': '2'
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
                'timeUpdated': '2021-01-04T14:32:20',
                'typeId': 1,
                'type_': {
                    'name': 'map',
                    'typeId': '1'
                },
                'updatingGitHubUser': {
                    'login': 'user1'
                }
            }
        }
    }
}

snapshots['test_schema_success[update] 2'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'path': 'site1:/path/to/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map2'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/map3'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site2:/another/way/beam1'
                    }
                },
                {
                    'node': {
                        'path': 'site1:/path/to/beam2'
                    }
                }
            ]
        },
        'allProductRelations': {
            'edges': [
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'map1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'map1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam1'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam1'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                }
            ]
        },
        'allProducts': {
            'edges': [
                {
                    'node': {
                        'name': 'map1'
                    }
                },
                {
                    'node': {
                        'name': 'map2'
                    }
                },
                {
                    'node': {
                        'name': 'map3'
                    }
                },
                {
                    'node': {
                        'name': 'beam1'
                    }
                },
                {
                    'node': {
                        'name': 'beam2'
                    }
                }
            ]
        }
    }
}
