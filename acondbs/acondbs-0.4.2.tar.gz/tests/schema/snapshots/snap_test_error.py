# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[one] 1'] = {
    'data': {
        'allLogs': {
            'edges': [
                {
                    'node': {
                        'id_': '1',
                        'level': 'ERROR',
                        'message': '''- Request:
    - Header:
        Content-Type:: application/json\r
        Authorization: Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f\r
        Remote-Addr: 127.0.0.1\r
        User-Agent: ASGI-Test-Client\r
        Host: localhost\r
        Content-Type: application/json\r
        Content-Length: 60

    - Data:
        - query:
            {
              noSuchField
            }

        - variables:
            {'var1': 100}

- Response:
    - Status:
        400 BAD REQUEST

    - Data:
            {
              "errors": [
                {
                  "message": "Cannot query field \\"noSuchField\\" on type \\"QueryAdmin\\".",
                  "locations": [
                    {
                      "line": 2,
                      "column": 3
                    }
                  ]
                }
              ]
            }
''',
                        'time': '2021-01-04T14:32:20'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
