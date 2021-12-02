# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error-no-name] 1'] = {
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

snapshots['test_schema_error[error-the-same-type-and-name] 1'] = {
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

snapshots['test_schema_success[create] 1'] = {
    'data': {
        'createProduct': {
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
                                'value': '2020-02-20'
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
                                'value': 'contact-person'
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
                                'value': 'producer'
                            }
                        }
                    ]
                },
                'name': 'beam111',
                'note': '- Item 1',
                'paths': {
                    'edges': [
                        {
                            'node': {
                                'note': None,
                                'path': '/path/to/new/product1',
                                'pathId': '9'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': '/another/location/of/product1',
                                'pathId': '10'
                            }
                        }
                    ]
                },
                'postingGitHubUser': {
                    'login': 'user1'
                },
                'productId': '6',
                'relations': {
                    'edges': [
                        {
                            'node': {
                                'other': {
                                    'name': 'map1',
                                    'productId': '1',
                                    'typeId': 1,
                                    'type_': {
                                        'name': 'map',
                                        'typeId': '1'
                                    }
                                },
                                'otherProductId': 1,
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
                                'relationId': '10',
                                'reverse': {
                                    'relationId': '9',
                                    'typeId': 2,
                                    'type_': {
                                        'name': 'child',
                                        'typeId': '2'
                                    }
                                },
                                'reverseRelationId': 9,
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
                'timeUpdated': None,
                'typeId': 2,
                'type_': {
                    'name': 'beam',
                    'typeId': '2'
                },
                'updatingGitHubUser': None
            }
        }
    }
}

snapshots['test_schema_success[create] 2'] = {
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
                },
                {
                    'node': {
                        'path': '/path/to/new/product1'
                    }
                },
                {
                    'node': {
                        'path': '/another/location/of/product1'
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
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam111'
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
                            'name': 'beam111'
                        },
                        'type_': {
                            'name': 'parent'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam111'
                        },
                        'self_': {
                            'name': 'beam2'
                        },
                        'type_': {
                            'name': 'child'
                        }
                    }
                },
                {
                    'node': {
                        'other': {
                            'name': 'beam2'
                        },
                        'self_': {
                            'name': 'beam111'
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
                },
                {
                    'node': {
                        'name': 'beam111'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[minimum] 1'] = {
    'data': {
        'createProduct': {
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
                                'value': None
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
                'name': 'product1',
                'note': None,
                'paths': {
                    'edges': [
                    ]
                },
                'postingGitHubUser': {
                    'login': 'user1'
                },
                'productId': '6',
                'relations': {
                    'edges': [
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
}

snapshots['test_schema_success[minimum] 2'] = {
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
                },
                {
                    'node': {
                        'name': 'product1'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[the-same-name-different-type] 1'] = {
    'data': {
        'createProduct': {
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
                                'value': None
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
                                'value': 'contact-person'
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
                                'value': 'pwg-pmn'
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
                                'path': '/path/to/new/product1',
                                'pathId': '9'
                            }
                        },
                        {
                            'node': {
                                'note': None,
                                'path': '/another/location/of/product1',
                                'pathId': '10'
                            }
                        }
                    ]
                },
                'postingGitHubUser': {
                    'login': 'user1'
                },
                'productId': '6',
                'relations': {
                    'edges': [
                    ]
                },
                'timePosted': '2021-01-04T14:32:20',
                'timeUpdated': None,
                'typeId': 2,
                'type_': {
                    'name': 'beam',
                    'typeId': '2'
                },
                'updatingGitHubUser': None
            }
        }
    }
}

snapshots['test_schema_success[the-same-name-different-type] 2'] = {
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
                },
                {
                    'node': {
                        'path': '/path/to/new/product1'
                    }
                },
                {
                    'node': {
                        'path': '/another/location/of/product1'
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
                },
                {
                    'node': {
                        'name': 'map1'
                    }
                }
            ]
        }
    }
}
