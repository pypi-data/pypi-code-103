# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema_success[one] 1'] = {
    'data': {
        'saveWebConfig': {
            'ok': True,
            'webConfig': {
                'id_': '1',
                'json': '''{
  "headTitle": "Saved Head Title",
  "toolbarTitle": "Saved Toolbar Title",
  "devtoolLoadingstate": false,
  "productCreationDialog": false,
  "productUpdateDialog": false,
  "productDeletionDialog": false
}'''
            }
        }
    }
}

snapshots['test_schema_success[one] 2'] = {
    'data': {
        'webConfig': {
            'id_': '1',
            'json': '''{
  "headTitle": "Saved Head Title",
  "toolbarTitle": "Saved Toolbar Title",
  "devtoolLoadingstate": false,
  "productCreationDialog": false,
  "productUpdateDialog": false,
  "productDeletionDialog": false
}'''
        }
    }
}
