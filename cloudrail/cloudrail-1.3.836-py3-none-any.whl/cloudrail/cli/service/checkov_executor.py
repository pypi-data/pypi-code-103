import copy
import logging
import os
from typing import List, Dict

import backoff


from common.api.dtos.checkov_result_dto import CheckovResultDTO


class CheckovExecutor:

    def execute_checkov(self, working_dir: str, checkov_rule_ids: List[str], base_dir: str) -> Dict[str, List[CheckovResultDTO]]:

        raw_results = self._safe_execute_checkov(working_dir, checkov_rule_ids)

        results = {}
        for raw_result in raw_results:
            for failed_check in raw_result.failed_checks:
                if not failed_check.file_line_range:
                    continue
                check_id = failed_check.check_id
                file_path = failed_check.file_path[1:] if failed_check.file_path.startswith('/') else failed_check.file_path
                file_path = os.path.join(base_dir, file_path) if base_dir else file_path
                checkov_result = CheckovResultDTO(check_id=failed_check.check_id,
                                                  file_path=file_path,
                                                  resource=failed_check.resource,
                                                  start_line=failed_check.file_line_range[0],
                                                  end_line=failed_check.file_line_range[1])
                logging.debug('found failed checkov result: {}'.format(vars(checkov_result)))
                if check_id not in results:
                    results[check_id] = []
                results[check_id].append(checkov_result)

        return results

    @staticmethod
    @backoff.on_exception(backoff.expo, Exception, max_time=60)
    def _safe_execute_checkov(working_dir: str, checkov_rule_ids: List[str]) -> list:
        from checkov.common.runners.runner_registry import RunnerRegistry
        from checkov.runner_filter import RunnerFilter
        from checkov.terraform.runner import Runner as tf_runner

        checkov_rule_ids = copy.deepcopy(checkov_rule_ids)
        runner_registry = RunnerRegistry('', RunnerFilter(checks=checkov_rule_ids), tf_runner())
        raw_results = runner_registry.run(working_dir)
        return raw_results
