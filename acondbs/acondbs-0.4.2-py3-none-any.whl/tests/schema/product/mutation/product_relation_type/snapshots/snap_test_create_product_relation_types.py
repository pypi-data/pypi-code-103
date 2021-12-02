# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error-already-exist] 1'] = {
    'data': {
        'allProductRelationTypes': {
            'edges': [
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'parent',
                        'plural': 'parents',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'child',
                            'typeId': '2'
                        },
                        'singular': 'parent',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'child',
                        'plural': 'children',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'parent',
                            'typeId': '1'
                        },
                        'singular': 'child',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'plaintiff',
                        'plural': 'plaintiffs',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'defendant',
                            'typeId': '4'
                        },
                        'singular': 'plaintiff',
                        'typeId': '3'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'defendant',
                        'plural': 'defendants',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'plaintiff',
                            'typeId': '3'
                        },
                        'singular': 'defendant',
                        'typeId': '4'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_error[error-reverse-and-self_reverse] 1'] = {
    'data': {
        'allProductRelationTypes': {
            'edges': [
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'parent',
                        'plural': 'parents',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'child',
                            'typeId': '2'
                        },
                        'singular': 'parent',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'child',
                        'plural': 'children',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'parent',
                            'typeId': '1'
                        },
                        'singular': 'child',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'plaintiff',
                        'plural': 'plaintiffs',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'defendant',
                            'typeId': '4'
                        },
                        'singular': 'plaintiff',
                        'typeId': '3'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'defendant',
                        'plural': 'defendants',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'plaintiff',
                            'typeId': '3'
                        },
                        'singular': 'defendant',
                        'typeId': '4'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[reverse] 1'] = {
    'data': {
        'createProductRelationTypes': {
            'ok': True,
            'productRelationType': {
                'indefArticle': 'a',
                'name': 'doctor',
                'plural': 'doctors',
                'relations': {
                    'edges': [
                    ]
                },
                'reverse': {
                    'name': 'patient',
                    'typeId': '6'
                },
                'singular': 'doctor',
                'typeId': '5'
            }
        }
    }
}

snapshots['test_schema_success[reverse] 2'] = {
    'data': {
        'allProductRelationTypes': {
            'edges': [
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'parent',
                        'plural': 'parents',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'child',
                            'typeId': '2'
                        },
                        'singular': 'parent',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'child',
                        'plural': 'children',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'parent',
                            'typeId': '1'
                        },
                        'singular': 'child',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'plaintiff',
                        'plural': 'plaintiffs',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'defendant',
                            'typeId': '4'
                        },
                        'singular': 'plaintiff',
                        'typeId': '3'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'defendant',
                        'plural': 'defendants',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'plaintiff',
                            'typeId': '3'
                        },
                        'singular': 'defendant',
                        'typeId': '4'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'doctor',
                        'plural': 'doctors',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'patient',
                            'typeId': '6'
                        },
                        'singular': 'doctor',
                        'typeId': '5'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'patient',
                        'plural': 'patients',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'doctor',
                            'typeId': '5'
                        },
                        'singular': 'patient',
                        'typeId': '6'
                    }
                }
            ]
        }
    }
}

snapshots['test_schema_success[self_reverse] 1'] = {
    'data': {
        'createProductRelationTypes': {
            'ok': True,
            'productRelationType': {
                'indefArticle': 'a',
                'name': 'spouse',
                'plural': 'spouses',
                'relations': {
                    'edges': [
                    ]
                },
                'reverse': {
                    'name': 'spouse',
                    'typeId': '5'
                },
                'singular': 'spouse',
                'typeId': '5'
            }
        }
    }
}

snapshots['test_schema_success[self_reverse] 2'] = {
    'data': {
        'allProductRelationTypes': {
            'edges': [
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'parent',
                        'plural': 'parents',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'map1',
                                            'productId': '1'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'child',
                            'typeId': '2'
                        },
                        'singular': 'parent',
                        'typeId': '1'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'child',
                        'plural': 'children',
                        'relations': {
                            'edges': [
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'map1',
                                            'productId': '1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'other': {
                                            'name': 'beam2',
                                            'productId': '5'
                                        },
                                        'self_': {
                                            'name': 'beam1',
                                            'productId': '4'
                                        }
                                    }
                                }
                            ]
                        },
                        'reverse': {
                            'name': 'parent',
                            'typeId': '1'
                        },
                        'singular': 'child',
                        'typeId': '2'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'plaintiff',
                        'plural': 'plaintiffs',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'defendant',
                            'typeId': '4'
                        },
                        'singular': 'plaintiff',
                        'typeId': '3'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'defendant',
                        'plural': 'defendants',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'plaintiff',
                            'typeId': '3'
                        },
                        'singular': 'defendant',
                        'typeId': '4'
                    }
                },
                {
                    'node': {
                        'indefArticle': 'a',
                        'name': 'spouse',
                        'plural': 'spouses',
                        'relations': {
                            'edges': [
                            ]
                        },
                        'reverse': {
                            'name': 'spouse',
                            'typeId': '5'
                        },
                        'singular': 'spouse',
                        'typeId': '5'
                    }
                }
            ]
        }
    }
}
