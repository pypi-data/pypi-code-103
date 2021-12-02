# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_error[error] 1'] = {
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

snapshots['test_schema_success[delete] 1'] = {
    'data': {
        'deleteProduct': {
            'ok': True
        }
    }
}

snapshots['test_schema_success[delete] 2'] = {
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
