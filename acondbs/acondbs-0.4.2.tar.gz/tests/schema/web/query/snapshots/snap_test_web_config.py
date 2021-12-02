# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[query] 1'] = {
    'data': {
        'webConfig': {
            'id_': '1',
            'json': '''{
  "headTitle": "Head Title",
  "toolbarTitle": "Toolbar Title",
  "devtoolLoadingstate": true,
  "productCreationDialog": false,
  "productUpdateDialog": true,
  "productDeletionDialog": true
}'''
        }
    }
}
