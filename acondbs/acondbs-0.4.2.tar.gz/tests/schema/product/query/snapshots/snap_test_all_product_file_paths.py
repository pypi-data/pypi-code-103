# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[all] 1'] = {
    'data': {
        'allProductFilePaths': {
            'edges': [
                {
                    'node': {
                        'note': None,
                        'path': 'site2:/another/way/map1',
                        'pathId': '1',
                        'product': {
                            'name': 'map1'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site1:/path/to/map2',
                        'pathId': '2',
                        'product': {
                            'name': 'map2'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site1:/path/to/map3',
                        'pathId': '3',
                        'product': {
                            'name': 'map3'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site2:/another/way/map3',
                        'pathId': '4',
                        'product': {
                            'name': 'map3'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site1:/path/to/beam1',
                        'pathId': '5',
                        'product': {
                            'name': 'beam1'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site2:/another/way/beam1',
                        'pathId': '6',
                        'product': {
                            'name': 'beam1'
                        }
                    }
                },
                {
                    'node': {
                        'note': None,
                        'path': 'site1:/path/to/beam2',
                        'pathId': '7',
                        'product': {
                            'name': 'beam2'
                        }
                    }
                },
                {
                    'node': {
                        'note': 'sample comment',
                        'path': 'site1:/path/to/map1',
                        'pathId': '8',
                        'product': {
                            'name': 'map1'
                        }
                    }
                }
            ],
            'totalCount': 8
        }
    }
}
