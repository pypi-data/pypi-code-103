from typing import List

from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase
from ai_api_client_sdk.models.scenario import Scenario


class TestE2EScenarios(AIAPIV2ClientE2ETestBase):

    @staticmethod
    def _get_scenario_from_scenarios(scenarios: List[Scenario], scenario_id: str):
        for s in scenarios:
            if s.id == scenario_id:
                return s
        return None

    def test_query_and_get_scenarios(self):
        response = self.ai_api_v2_client.scenario.query()
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        queried_scenario = self._get_scenario_from_scenarios(scenarios, self.test_scenario_id)
        scenario = self.ai_api_v2_client.scenario.get(scenario_id=self.test_scenario_id)
        self.assertEqual(queried_scenario, scenario)
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)
        self.assertIsNotNone(scenario.created_at)
        self.assertIsNotNone(scenario.modified_at)

    def test_query_versions(self):
        version_response = self.ai_api_v2_client.scenario.query_versions(scenario_id=self.test_scenario_id)
        self.assertTrue(version_response.count > 0)
        self.assertEqual(version_response.count, len(version_response.resources))
        version = version_response.resources[0]
        self.assertIsNotNone(version.id)
        self.assertIsNotNone(version.scenario_id)
        self.assertIsNotNone(version.created_at)
        self.assertIsNotNone(version.modified_at)
