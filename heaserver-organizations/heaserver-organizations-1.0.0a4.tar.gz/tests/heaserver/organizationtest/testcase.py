"""
Creates a test case class for use with the unittest library that is built into Python.
"""

from heaserver.service.testcase.mockmongotestcase import get_test_case_cls_default
from heaserver.organization import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import ActionSpec

db_store = {
    service.MONGODB_ORGANIZATION_COLLECTION: [
        {
            "id": "666f6f2d6261722d71757578",
            "source": None,
            "name": "Bob",
            "display_name": "Bob",
            "description": "Description of Bob",
            "owner": NONE_USER,
            "created": None,
            "modified": None,
            "invites": [],
            "shares": [],
            "derived_by": None,
            "derived_from": [],
            "aws_account_ids": [],
            "principal_investigator_id": "23423DAFSDF12adfasdf3",
            "manager_ids": [],
            "member_ids": [],
            'type': 'heaobject.organization.Organization',
            'version': None
        },
        {
            "id": "0123456789ab0123456789ab",
            "source": None,
            "name": "Reximus",
            "display_name": "Reximus",
            "description": "Description of Reximus",
            "owner": NONE_USER,
            "created": None,
            "modified": None,
            "invites": [],
            "shares": [],
            "derived_by": None,
            "derived_from": [],
            "aws_account_ids": [],
            "principal_investigator_id": "11234867890b0123a56789ab",
            "manager_ids": ["11234867890b0123a56789ab"],
            "member_ids": [],
            'type': 'heaobject.organization.Organization',
            'version': None
        }
    ]}

TestCase = get_test_case_cls_default(coll=service.MONGODB_ORGANIZATION_COLLECTION,
                                     wstl_package=service.__package__,
                                     href='http://localhost:8080/organizations/',
                                     fixtures=db_store,
                                     get_actions=[ActionSpec(name='heaserver-organizations-organization-get-properties',
                                                             rel=['properties']),
                                                  ActionSpec(name='heaserver-organizations-organization-get-open-choices',
                                                             url='/organizations/{id}/opener',
                                                             rel=['hea-opener-choices']),
                                                  ActionSpec(name='heaserver-organizations-organization-duplicate',
                                                             url='/organizations/{id}/duplicator',
                                                             rel=['duplicator'])
                                                  ],
                                     get_all_actions=[ActionSpec(name='heaserver-organizations-organization-get-properties',
                                                                 rel=['properties']),
                                                      ActionSpec(name='heaserver-organizations-organization-get-open-choices',
                                                                 url='/organizations/{id}/opener',
                                                                 rel=['hea-opener-choices']),
                                                      ActionSpec(name='heaserver-organizations-organization-duplicate',
                                                                 url='/organizations/{id}/duplicator',
                                                                 rel=['duplicator'])],
                                     duplicate_action_name='heaserver-organizations-organization-duplicate-form')
