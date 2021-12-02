# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error-nonexistent] 1'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-spotlight-beam',
                        'indefArticle': 'a',
                        'name': 'beam',
                        'order': 1,
                        'plural': 'beams',
                        'products': {
                            'edges': [
                            ]
                        },
                        'singular': 'beam',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'map'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'map'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'map'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-map',
                        'indefArticle': 'a',
                        'name': 'map',
                        'order': 2,
                        'plural': 'maps',
                        'products': {
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
                                }
                            ]
                        },
                        'singular': 'map',
                        'typeId': '1'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['test_schema_success[empty-fields] 1'] = {
    'data': {
        'updateProductType': {
            'ok': True,
            'productType': {
                'fields': {
                    'edges': [
                    ]
                },
                'icon': 'mdi-compass',
                'indefArticle': 'a',
                'name': 'compass',
                'order': 5,
                'plural': 'compasses',
                'products': {
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
                        }
                    ]
                },
                'singular': 'compass',
                'typeId': '1'
            }
        }
    }
}

snapshots['test_schema_success[empty-fields] 2'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-spotlight-beam',
                        'indefArticle': 'a',
                        'name': 'beam',
                        'order': 1,
                        'plural': 'beams',
                        'products': {
                            'edges': [
                            ]
                        },
                        'singular': 'beam',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'fields': {
                            'edges': [
                            ]
                        },
                        'icon': 'mdi-compass',
                        'indefArticle': 'a',
                        'name': 'compass',
                        'order': 5,
                        'plural': 'compasses',
                        'products': {
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
                                }
                            ]
                        },
                        'singular': 'compass',
                        'typeId': '1'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['test_schema_success[fields-unchanged] 1'] = {
    'data': {
        'updateProductType': {
            'ok': True,
            'productType': {
                'fields': {
                    'edges': [
                        {
                            'node': {
                                'field': {
                                    'name': 'contact',
                                    'type_': 'UNICODE_TEXT'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        },
                        {
                            'node': {
                                'field': {
                                    'name': 'produced_by',
                                    'type_': 'UNICODE_TEXT'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        },
                        {
                            'node': {
                                'field': {
                                    'name': 'date_produced',
                                    'type_': 'DATE'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        }
                    ]
                },
                'icon': 'mdi-compass',
                'indefArticle': 'a',
                'name': 'compass',
                'order': 5,
                'plural': 'compasses',
                'products': {
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
                        }
                    ]
                },
                'singular': 'compass',
                'typeId': '1'
            }
        }
    }
}

snapshots['test_schema_success[fields-unchanged] 2'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-spotlight-beam',
                        'indefArticle': 'a',
                        'name': 'beam',
                        'order': 1,
                        'plural': 'beams',
                        'products': {
                            'edges': [
                            ]
                        },
                        'singular': 'beam',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-compass',
                        'indefArticle': 'a',
                        'name': 'compass',
                        'order': 5,
                        'plural': 'compasses',
                        'products': {
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
                                }
                            ]
                        },
                        'singular': 'compass',
                        'typeId': '1'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['test_schema_success[update] 1'] = {
    'data': {
        'updateProductType': {
            'ok': True,
            'productType': {
                'fields': {
                    'edges': [
                        {
                            'node': {
                                'field': {
                                    'name': 'contact',
                                    'type_': 'UNICODE_TEXT'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        },
                        {
                            'node': {
                                'field': {
                                    'name': 'field_four',
                                    'type_': 'UNICODE_TEXT'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        },
                        {
                            'node': {
                                'field': {
                                    'name': 'field_five',
                                    'type_': 'UNICODE_TEXT'
                                },
                                'type_': {
                                    'name': 'compass'
                                }
                            }
                        }
                    ]
                },
                'icon': 'mdi-compass',
                'indefArticle': 'a',
                'name': 'compass',
                'order': 5,
                'plural': 'compasses',
                'products': {
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
                        }
                    ]
                },
                'singular': 'compass',
                'typeId': '1'
            }
        }
    }
}

snapshots['test_schema_success[update] 2'] = {
    'data': {
        'allProductTypes': {
            'edges': [
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'produced_by',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'date_produced',
                                            'type_': 'DATE'
                                        },
                                        'type_': {
                                            'name': 'beam'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-spotlight-beam',
                        'indefArticle': 'a',
                        'name': 'beam',
                        'order': 1,
                        'plural': 'beams',
                        'products': {
                            'edges': [
                            ]
                        },
                        'singular': 'beam',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'fields': {
                            'edges': [
                                {
                                    'node': {
                                        'field': {
                                            'name': 'contact',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'field_four',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'field': {
                                            'name': 'field_five',
                                            'type_': 'UNICODE_TEXT'
                                        },
                                        'type_': {
                                            'name': 'compass'
                                        }
                                    }
                                }
                            ]
                        },
                        'icon': 'mdi-compass',
                        'indefArticle': 'a',
                        'name': 'compass',
                        'order': 5,
                        'plural': 'compasses',
                        'products': {
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
                                }
                            ]
                        },
                        'singular': 'compass',
                        'typeId': '1'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}
