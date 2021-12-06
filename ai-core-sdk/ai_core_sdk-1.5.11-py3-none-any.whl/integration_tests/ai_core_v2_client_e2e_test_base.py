from unittest import TestCase
from typing import Any, Dict

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from . import AUTH_URL, BASE_URL, CLIENT_ID, CLIENT_SECRET, RESOURCE_GROUP_ID


class AICoreV2ClientE2ETestBase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Uncomment the following line and the one in tearDownClass to run integration_tests via IDE (against intwdf)
        # provision_resource_group()
        cls.ai_core_v2_client = AICoreV2Client(base_url=BASE_URL, auth_url=AUTH_URL, client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET, resource_group=RESOURCE_GROUP_ID)
        cls.test_scenario_id = '88888888-4444-4444-4444-cccccccccccc'

    @classmethod
    def tearDownClass(cls) -> None:
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE (against intwdf)
        # deprovision_resource_group()
        super().tearDownClass()

    def assert_object(self, d: Dict[str, Any], o: object):
        for k in d.keys():
            self.assertEqual(d[k], getattr(o, k))
