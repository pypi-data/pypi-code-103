from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus


class TestE2EDeployments(AIAPIV2ClientE2ETestBase):
    def test_deployments(self):
        configuration = self.get_a_configuration(deployable=True)
        n = 2
        deployment_dicts = []
        for _ in range(n):
            res = self.ai_api_v2_client.deployment.create(configuration_id=configuration.id)
            deployment_dicts.append({
                'id': res.id,
                'configuration_id': configuration.id,
                'configuration_name': configuration.name,
                'scenario_id': self.test_scenario_id
            })
        for dep_dict in deployment_dicts:
            dep = self.ai_api_v2_client.deployment.get(deployment_id=dep_dict['id'])
            self.assert_object(dep_dict, dep)
            self.assertIsNotNone(dep.created_at)
            dep_dict['created_at'] = dep.created_at
            self.assertIsNotNone(dep.modified_at)
            self.assertEqual(TargetStatus.RUNNING, dep.target_status)
            dep_dict['target_status'] = dep.target_status
            dep = self.wait_until_enactment_has_status(resource_client=self.ai_api_v2_client.deployment,
                                                       params={'deployment_id': dep_dict['id']}, status=Status.RUNNING)
            dep_dict['status'] = dep.status
            self.assertIsNotNone(dep.deployment_url)
            self.assertNotEqual('', dep.deployment_url)
            dep_dict['deployment_url'] = dep.deployment_url

            logs = self.ai_api_v2_client.deployment.query_logs(deployment_id=dep_dict['id'])
            self.assertIsNotNone(logs.data.result)

        res = self.ai_api_v2_client.deployment.query(scenario_id=self.test_scenario_id,
                                                     configuration_id=configuration.id,
                                                     executable_ids=[configuration.executable_id],
                                                     status=Status.RUNNING)
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(deployment_dicts, res.resources)

        res_count = self.ai_api_v2_client.deployment.count(scenario_id=self.test_scenario_id,
                                                     configuration_id=configuration.id,
                                                     executable_ids=[configuration.executable_id],
                                                     status=Status.RUNNING)
        self.assertTrue(res_count >= n)
