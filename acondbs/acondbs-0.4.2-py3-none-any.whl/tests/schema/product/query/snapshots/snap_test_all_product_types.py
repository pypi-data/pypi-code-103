# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[sort-order] 1'] = {
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
