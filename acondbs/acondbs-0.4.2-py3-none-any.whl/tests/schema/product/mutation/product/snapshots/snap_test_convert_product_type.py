# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_success[convert] 1'] = {
    'data': {
        'convertProductType': {
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

snapshots['test_schema_success[convert] 2'] = {
    'data': {
        'allProducts': {
            'edges': [
                {
                    'node': {
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
                        'typeId': 2,
                        'type_': {
                            'name': 'beam',
                            'typeId': '2'
                        },
                        'updatingGitHubUser': {
                            'login': 'user1'
                        }
                    }
                },
                {
                    'node': {
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
                                        'value': '2020-02-10'
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
                        'name': 'map2',
                        'note': None,
                        'paths': {
                            'edges': [
                                {
                                    'node': {
                                        'note': None,
                                        'path': 'site1:/path/to/map2',
                                        'pathId': '3'
                                    }
                                }
                            ]
                        },
                        'postingGitHubUser': None,
                        'productId': '2',
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
                },
                {
                    'node': {
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
                                        'value': '2020-03-19'
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
                        'name': 'map3',
                        'note': None,
                        'paths': {
                            'edges': [
                                {
                                    'node': {
                                        'note': None,
                                        'path': 'site1:/path/to/map3',
                                        'pathId': '4'
                                    }
                                },
                                {
                                    'node': {
                                        'note': None,
                                        'path': 'site2:/another/way/map3',
                                        'pathId': '5'
                                    }
                                }
                            ]
                        },
                        'postingGitHubUser': None,
                        'productId': '3',
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
                },
                {
                    'node': {
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
                                        'value': '2020-02-05'
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
                        'name': 'beam1',
                        'note': None,
                        'paths': {
                            'edges': [
                                {
                                    'node': {
                                        'note': None,
                                        'path': 'site1:/path/to/beam1',
                                        'pathId': '6'
                                    }
                                },
                                {
                                    'node': {
                                        'note': None,
                                        'path': 'site2:/another/way/beam1',
                                        'pathId': '7'
                                    }
                                }
                            ]
                        },
                        'postingGitHubUser': None,
                        'productId': '4',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1',
                                            'typeId': 2,
                                            'type_': {
                                                'name': 'beam',
                                                'typeId': '2'
                                            }
                                        },
                                        'otherProductId': 1,
                                        'relationId': '2',
                                        'reverse': {
                                            'relationId': '1',
                                            'typeId': 2,
                                            'type_': {
                                                'name': 'child',
                                                'typeId': '2'
                                            }
                                        },
                                        'reverseRelationId': 1,
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
                                        'relationId': '5',
                                        'reverse': {
                                            'relationId': '6',
                                            'typeId': 1,
                                            'type_': {
                                                'name': 'parent',
                                                'typeId': '1'
                                            }
                                        },
                                        'reverseRelationId': 6,
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
                        'typeId': 2,
                        'type_': {
                            'name': 'beam',
                            'typeId': '2'
                        },
                        'updatingGitHubUser': None
                    }
                },
                {
                    'node': {
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
                                            'name': 'map1',
                                            'productId': '1',
                                            'typeId': 2,
                                            'type_': {
                                                'name': 'beam',
                                                'typeId': '2'
                                            }
                                        },
                                        'otherProductId': 1,
                                        'relationId': '4',
                                        'reverse': {
                                            'relationId': '3',
                                            'typeId': 2,
                                            'type_': {
                                                'name': 'child',
                                                'typeId': '2'
                                            }
                                        },
                                        'reverseRelationId': 3,
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
            ]
        }
    }
}
