# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[name] 1'] = {
    'data': {
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
}

snapshots['test_schema[type_id-and-name-nonexistent] 1'] = {
    'data': {
        'productType': None
    }
}

snapshots['test_schema[type_id-and-name] 1'] = {
    'data': {
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
}

snapshots['test_schema[type_id-sort-products] 1'] = {
    'data': {
        'productType': {
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
}

snapshots['test_schema[type_id] 1'] = {
    'data': {
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
}
