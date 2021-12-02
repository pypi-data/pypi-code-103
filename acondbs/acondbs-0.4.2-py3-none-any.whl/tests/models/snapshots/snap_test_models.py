# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_table_names 1'] = [
    'product_types',
    'products',
    'product_file_paths',
    'product_relation_types',
    'product_relations',
    'attribute_unicode_text',
    'attribute_boolean',
    'attribute_integer',
    'attribute_float',
    'attribute_date',
    'attribute_date_time',
    'attribute_time',
    'field',
    'type_field_association',
    'github_tokens',
    'github_orgs',
    'github_users',
    'github_org_memberships',
    'account_admins',
    'web_config',
    'log'
]
