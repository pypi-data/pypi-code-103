# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[name] 1'] = {
    'data': {
        'productRelationType': {
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
    }
}

snapshots['test_schema[type_id-and-name-nonexistent)] 1'] = {
    'data': {
        'productRelationType': None
    }
}

snapshots['test_schema[type_id-and-name] 1'] = {
    'data': {
        'productRelationType': {
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
    }
}

snapshots['test_schema[type_id] 1'] = {
    'data': {
        'productRelationType': {
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
    }
}
