# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_export_db_to_csv_files 1'] = {
    'account_admins': [
    ],
    'attribute_boolean': [
    ],
    'attribute_date': [
        {
            'field_id': 3,
            'iid': 1,
            'product_id': 1001,
            'type_field_association_iid': 3,
            'value': GenericRepr('datetime.date(2019, 2, 13)')
        },
        {
            'field_id': 3,
            'iid': 2,
            'product_id': 1002,
            'type_field_association_iid': 9,
            'value': GenericRepr('datetime.date(2019, 3, 15)')
        },
        {
            'field_id': 3,
            'iid': 3,
            'product_id': 1010,
            'type_field_association_iid': 6,
            'value': GenericRepr('datetime.date(2018, 1, 1)')
        },
        {
            'field_id': 3,
            'iid': 4,
            'product_id': 1012,
            'type_field_association_iid': 3,
            'value': GenericRepr('datetime.date(2020, 1, 20)')
        },
        {
            'field_id': 3,
            'iid': 5,
            'product_id': 1013,
            'type_field_association_iid': 3,
            'value': GenericRepr('datetime.date(2020, 2, 1)')
        },
        {
            'field_id': 3,
            'iid': 6,
            'product_id': 1070,
            'type_field_association_iid': 6,
            'value': GenericRepr('datetime.date(2019, 3, 4)')
        },
        {
            'field_id': 3,
            'iid': 7,
            'product_id': 1120,
            'type_field_association_iid': 6,
            'value': GenericRepr('datetime.date(2019, 6, 7)')
        },
        {
            'field_id': 3,
            'iid': 8,
            'product_id': 1130,
            'type_field_association_iid': 6,
            'value': GenericRepr('datetime.date(2020, 1, 23)')
        },
        {
            'field_id': 3,
            'iid': 9,
            'product_id': 1150,
            'type_field_association_iid': 6,
            'value': GenericRepr('datetime.date(2020, 2, 7)')
        }
    ],
    'attribute_date_time': [
    ],
    'attribute_float': [
    ],
    'attribute_integer': [
    ],
    'attribute_time': [
    ],
    'attribute_unicode_text': [
        {
            'field_id': 1,
            'iid': 2,
            'product_id': 1001,
            'type_field_association_iid': 1,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 3,
            'product_id': 1001,
            'type_field_association_iid': 2,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 8,
            'product_id': 1002,
            'type_field_association_iid': 7,
            'value': 'abc-def'
        },
        {
            'field_id': 2,
            'iid': 9,
            'product_id': 1002,
            'type_field_association_iid': 8,
            'value': 'abc-def'
        },
        {
            'field_id': 1,
            'iid': 14,
            'product_id': 1010,
            'type_field_association_iid': 4,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 15,
            'product_id': 1010,
            'type_field_association_iid': 5,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 20,
            'product_id': 1012,
            'type_field_association_iid': 1,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 21,
            'product_id': 1012,
            'type_field_association_iid': 2,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 26,
            'product_id': 1013,
            'type_field_association_iid': 1,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 27,
            'product_id': 1013,
            'type_field_association_iid': 2,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 32,
            'product_id': 1070,
            'type_field_association_iid': 4,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 33,
            'product_id': 1070,
            'type_field_association_iid': 5,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 38,
            'product_id': 1120,
            'type_field_association_iid': 4,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 39,
            'product_id': 1120,
            'type_field_association_iid': 5,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 44,
            'product_id': 1130,
            'type_field_association_iid': 4,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 45,
            'product_id': 1130,
            'type_field_association_iid': 5,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 1,
            'iid': 50,
            'product_id': 1150,
            'type_field_association_iid': 4,
            'value': 'pwg-pmn'
        },
        {
            'field_id': 2,
            'iid': 51,
            'product_id': 1150,
            'type_field_association_iid': 5,
            'value': 'pwg-pmn'
        }
    ],
    'field': [
        {
            'field_id': 1,
            'name': 'contact',
            'type_': 'UnicodeText'
        },
        {
            'field_id': 2,
            'name': 'produced_by',
            'type_': 'UnicodeText'
        },
        {
            'field_id': 3,
            'name': 'date_produced',
            'type_': 'Date'
        }
    ],
    'github_org_memberships': [
    ],
    'github_orgs': [
        {
            'avatar_url': 'https://avatars0.githubusercontent.com/u/75631844?v=4',
            'git_hub_id': '012:Organization75631844',
            'login': 'urban-octo-disco',
            'org_id': 1,
            'url': 'https://github.com/urban-octo-disco'
        }
    ],
    'github_tokens': [
        {
            'scope': 'read:org',
            'time_created': GenericRepr('datetime.datetime(2020, 1, 4, 14, 32, 15)'),
            'token': b'aKjGknYDHY39Z2xAaN7+sQ==',
            'token_id': 1,
            'user_id': 1
        }
    ],
    'github_users': [
        {
            'avatar_url': 'https://avatars3.githubusercontent.com/u/583231?v=4',
            'git_hub_id': '04:User583231',
            'login': 'octocat',
            'name': 'The Octocat',
            'url': 'https://github.com/octocat',
            'user_id': 1
        },
        {
            'avatar_url': 'https://avatars0.githubusercontent.com/u/9758946?v=4',
            'git_hub_id': '04:User9758946',
            'login': 'dojocat',
            'name': 'dojocat',
            'url': 'https://github.com/dojocat',
            'user_id': 2
        }
    ],
    'log': [
    ],
    'product_file_paths': [
        {
            'note': '',
            'path': 'nersc:/go/to/my/maps',
            'path_id': 1,
            'product_id': 1001
        },
        {
            'note': 'lat only',
            'path': 'nersc:/go/to/my/maps_v2',
            'path_id': 2,
            'product_id': 1012
        },
        {
            'note': 'lat only',
            'path': 'abcde:/path/to/the/maps_v2',
            'path_id': 3,
            'product_id': 1012
        },
        {
            'note': 'lat only',
            'path': 'nersc:/go/to/my/maps_v3',
            'path_id': 4,
            'product_id': 1013
        },
        {
            'note': '',
            'path': 'BEAM_DEPOT/Beams/20190304',
            'path_id': 5,
            'product_id': 1070
        },
        {
            'note': '',
            'path': 'BEAM_DEPOT/Beams/20190607',
            'path_id': 6,
            'product_id': 1120
        },
        {
            'note': '',
            'path': 'BEAM_DEPOT/Beams/20200123',
            'path_id': 7,
            'product_id': 1130
        },
        {
            'note': '',
            'path': 'BEAM_DEPOT/Beams/20200207',
            'path_id': 8,
            'product_id': 1150
        },
        {
            'note': '',
            'path': 'nersc:/go/to/my/simulations',
            'path_id': 9,
            'product_id': 1002
        },
        {
            'note': '',
            'path': 'abcde:/path/to/the/simulations',
            'path_id': 10,
            'product_id': 1002
        }
    ],
    'product_relation_types': [
        {
            'indef_article': 'a',
            'name': 'parent',
            'plural': 'parents',
            'reverse_type_id': 2,
            'singular': 'parent',
            'type_id': 1
        },
        {
            'indef_article': 'a',
            'name': 'child',
            'plural': 'children',
            'reverse_type_id': 1,
            'singular': 'child',
            'type_id': 2
        },
        {
            'indef_article': 'a',
            'name': 'plaintiff',
            'plural': 'plaintiffs',
            'reverse_type_id': 4,
            'singular': 'plaintiff',
            'type_id': 3
        },
        {
            'indef_article': 'a',
            'name': 'defendant',
            'plural': 'defendants',
            'reverse_type_id': 3,
            'singular': 'defendant',
            'type_id': 4
        }
    ],
    'product_relations': [
        {
            'other_product_id': 1012,
            'relation_id': 1,
            'reverse_relation_id': 2,
            'self_product_id': 1130,
            'type_id': 1
        },
        {
            'other_product_id': 1130,
            'relation_id': 2,
            'reverse_relation_id': 1,
            'self_product_id': 1012,
            'type_id': 2
        },
        {
            'other_product_id': 1013,
            'relation_id': 3,
            'reverse_relation_id': 4,
            'self_product_id': 1150,
            'type_id': 1
        },
        {
            'other_product_id': 1150,
            'relation_id': 4,
            'reverse_relation_id': 3,
            'self_product_id': 1013,
            'type_id': 2
        },
        {
            'other_product_id': 1130,
            'relation_id': 5,
            'reverse_relation_id': 6,
            'self_product_id': 1150,
            'type_id': 1
        },
        {
            'other_product_id': 1150,
            'relation_id': 6,
            'reverse_relation_id': 5,
            'self_product_id': 1130,
            'type_id': 2
        }
    ],
    'product_types': [
        {
            'icon': 'mdi-map',
            'indef_article': 'a',
            'name': 'map',
            'order': 2,
            'plural': 'maps',
            'singular': 'map',
            'type_id': 1
        },
        {
            'icon': 'mdi-spotlight-beam',
            'indef_article': 'a',
            'name': 'beam',
            'order': 3,
            'plural': 'beams',
            'singular': 'beam',
            'type_id': 2
        },
        {
            'icon': 'mdi-creation',
            'indef_article': 'a',
            'name': 'simulation',
            'order': 1,
            'plural': 'simulations',
            'singular': 'simulation',
            'type_id': 3
        },
        {
            'icon': '',
            'indef_article': '',
            'name': 'anchor',
            'order': 4,
            'plural': '',
            'singular': '',
            'type_id': 4
        }
    ],
    'products': [
        {
            'name': 'lat20190213',
            'note': '''- This is a dummy test with a lat map
- This should not depend on any beam''',
            'posting_git_hub_user_id': 1,
            'product_id': 1001,
            'time_posted': GenericRepr('datetime.datetime(2019, 2, 13, 10, 5, 23)'),
            'time_updated': None,
            'type_id': 1,
            'updating_git_hub_user_id': 2
        },
        {
            'name': 'xyz-s1234-20200101',
            'note': '''- note 1
- note 2''',
            'posting_git_hub_user_id': 1,
            'product_id': 1002,
            'time_posted': GenericRepr('datetime.datetime(2019, 3, 15, 9, 11, 25)'),
            'time_updated': None,
            'type_id': 3,
            'updating_git_hub_user_id': None
        },
        {
            'name': '20180101',
            'note': '- test entry',
            'posting_git_hub_user_id': 1,
            'product_id': 1010,
            'time_posted': GenericRepr('datetime.datetime(2018, 1, 1, 15, 32, 10)'),
            'time_updated': None,
            'type_id': 2,
            'updating_git_hub_user_id': None
        },
        {
            'name': 'lat20200120',
            'note': '''- This is a dummy test with a lat map
- A beam depends on this map''',
            'posting_git_hub_user_id': 1,
            'product_id': 1012,
            'time_posted': GenericRepr('datetime.datetime(2020, 1, 20, 18, 10, 5)'),
            'time_updated': None,
            'type_id': 1,
            'updating_git_hub_user_id': 2
        },
        {
            'name': 'lat20200201',
            'note': '''- This is a dummy test with a lat map
- A beam depends on this map''',
            'posting_git_hub_user_id': 1,
            'product_id': 1013,
            'time_posted': GenericRepr('datetime.datetime(2020, 2, 1, 11, 5, 2)'),
            'time_updated': None,
            'type_id': 1,
            'updating_git_hub_user_id': 2
        },
        {
            'name': '20190304',
            'note': '- test entry',
            'posting_git_hub_user_id': 1,
            'product_id': 1070,
            'time_posted': GenericRepr('datetime.datetime(2019, 3, 4, 8, 12, 41)'),
            'time_updated': None,
            'type_id': 2,
            'updating_git_hub_user_id': None
        },
        {
            'name': '20190607',
            'note': '- test entry',
            'posting_git_hub_user_id': 1,
            'product_id': 1120,
            'time_posted': GenericRepr('datetime.datetime(2019, 6, 7, 18, 21, 21)'),
            'time_updated': None,
            'type_id': 2,
            'updating_git_hub_user_id': None
        },
        {
            'name': '20200123',
            'note': '- test entry',
            'posting_git_hub_user_id': 1,
            'product_id': 1130,
            'time_posted': GenericRepr('datetime.datetime(2020, 1, 23, 12, 11, 45)'),
            'time_updated': None,
            'type_id': 2,
            'updating_git_hub_user_id': None
        },
        {
            'name': '20200207',
            'note': '- test entry',
            'posting_git_hub_user_id': 1,
            'product_id': 1150,
            'time_posted': GenericRepr('datetime.datetime(2020, 2, 7, 9, 42, 11)'),
            'time_updated': None,
            'type_id': 2,
            'updating_git_hub_user_id': None
        }
    ],
    'type_field_association': [
        {
            'field_id': 1,
            'iid': 1,
            'order': None,
            'type_id': 1
        },
        {
            'field_id': 2,
            'iid': 2,
            'order': None,
            'type_id': 1
        },
        {
            'field_id': 3,
            'iid': 3,
            'order': None,
            'type_id': 1
        },
        {
            'field_id': 1,
            'iid': 4,
            'order': None,
            'type_id': 2
        },
        {
            'field_id': 2,
            'iid': 5,
            'order': None,
            'type_id': 2
        },
        {
            'field_id': 3,
            'iid': 6,
            'order': None,
            'type_id': 2
        },
        {
            'field_id': 1,
            'iid': 7,
            'order': None,
            'type_id': 3
        },
        {
            'field_id': 2,
            'iid': 8,
            'order': None,
            'type_id': 3
        },
        {
            'field_id': 3,
            'iid': 9,
            'order': None,
            'type_id': 3
        },
        {
            'field_id': 1,
            'iid': 10,
            'order': None,
            'type_id': 4
        },
        {
            'field_id': 2,
            'iid': 11,
            'order': None,
            'type_id': 4
        },
        {
            'field_id': 3,
            'iid': 12,
            'order': None,
            'type_id': 4
        }
    ],
    'web_config': [
        {
            'id_': 1,
            'json': '{"headTitle": "Product DB (test)", "toolbarTitle": "Product DB (test)", "devtoolLoadingstate": true, "productCreationDialog": false, "productUpdateDialog": true, "productDeletionDialog": false}'
        }
    ]
}
