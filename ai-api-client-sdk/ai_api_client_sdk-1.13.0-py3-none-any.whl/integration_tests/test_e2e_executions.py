from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus


class TestE2EExecutions(AIAPIV2ClientE2ETestBase):
    def test_executions(self):
        configuration = self.get_a_configuration(deployable=False)
        n = 3
        execution_dicts = []
        for _ in range(n):
            res = self.ai_api_v2_client.execution.create(configuration_id=configuration.id)
            execution_dicts.append({
                'id': res.id,
                'configuration_id': configuration.id,
                'configuration_name': configuration.name,
                'scenario_id': self.test_scenario_id
            })
        for execution_dict in execution_dicts:
            execution = self.ai_api_v2_client.execution.get(execution_id=execution_dict['id'])
            self.assert_object(execution_dict, execution)
            self.assertIsNotNone(execution.created_at)
            execution_dict['created_at'] = execution.created_at
            self.assertIsNotNone(execution.modified_at)
            self.assertEqual(TargetStatus.COMPLETED, execution.target_status)
            execution_dict['target_status'] = execution.target_status
            execution = self.wait_until_enactment_has_status(resource_client=self.ai_api_v2_client.execution,
                                                             params={'execution_id': execution_dict['id']},
                                                             status=Status.COMPLETED)
            execution_dict['status'] = execution.status
            logs = self.ai_api_v2_client.execution.query_logs(execution_id=execution_dict['id'])
            self.assertIsNotNone(logs.data.result)

        res = self.ai_api_v2_client.execution.query(scenario_id=self.test_scenario_id,
                                                    configuration_id=configuration.id,
                                                    executable_ids=[configuration.executable_id],
                                                    status=Status.COMPLETED)
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(execution_dicts, res.resources)

        res_count = self.ai_api_v2_client.execution.count(scenario_id=self.test_scenario_id,
                                                    configuration_id=configuration.id,
                                                    executable_ids=[configuration.executable_id],
                                                    status=Status.COMPLETED)
        self.assertTrue(res_count >= n)
