import json
import os
import re
from itertools import chain
from typing import List

import pytest_testrail_api_client.configure as configure
from pytest_testrail_api_client.client_config import TR_PREFIX
from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.modules.plan import Run, Plan
from pytest_testrail_api_client.modules.result import Result
from pytest_testrail_api_client.service import to_json, trim, sort_configurations


class ServiceApi(Base):
    def convert_configs_to_ids(self, configs: (str, list)):
        all_configs = tuple(chain.from_iterable((x.configs for x in self._session.configs.get_configs())))
        if isinstance(configs, str):
            configs = configure.trim(configs).split(', ')
        config_ids = []
        for config in configs:
            config_id = [conf_id.id for conf_id in all_configs if conf_id.name.lower() == config.lower()]
            if len(config_id) > 0:
                config_ids.append(config_id[0])
        return config_ids

    def get_suite_by_name(self, suite_name: str, suite_list: List[Suite] = None) -> Suite:
        suite_list = self._session.suites.get_suites() if suite_list is None else suite_list
        result = tuple(suite for suite in suite_list if suite.name.lower() == suite_name.lower())
        return result[0] if len(result) > 0 else []

    def delete_untested_tests_from_run(self, run_id: int):
        case_ids = list(result.case_id for result in self._session.tests.get_tests(run_id, status_id='1, 5'))
        self._session.plans.update_run_in_plan_entry(run_id=run_id, include_all=False, case_ids=case_ids)

    def copy_run_to_plan(self, run_id: int, plan_id: int, delete_untested: bool = True,
                         delete_original_run: bool = False, milestone_id: int = None) -> Run:
        run = self._session.runs.get_run(run_id)
        run_tests = self._session.tests.get_tests(run_id)
        cases_ids = tuple(test.case_id for test in run_tests)
        run_to_add = {'include_all': False, 'config_ids': run.config_ids, 'case_ids': cases_ids}
        if milestone_id is not None and isinstance(milestone_id, int):
            run_to_add.update({'milestone_id': milestone_id})
        new_entry = self._session.plans.add_plan_entry(plan_id, suite_id=run.suite_id, name=run.name,
                                                       description=run.description, config_ids=run.config_ids,
                                                       runs=[run_to_add])
        new_run_id = new_entry.runs[-1].id

        self.copy_results_from_run(run_id, new_run_id, run_tests)
        if delete_untested is True:
            self.delete_untested_tests_from_run(new_run_id)
        if delete_original_run is True:
            self._session.runs.delete_run(run_id)

        return new_entry.runs[-1]

    def copy_results_from_run(self, old_run_id: int, new_run_id: int, old_tests: List[Result] = None,
                              status_id: list = None, overwrite_results: list = None):
        if status_id is not None:
            statuses = tuple(status.id for status in self._session.statuses.get_statuses() if status.id in status_id)
        else:
            statuses = tuple(status.id for status in self._session.statuses.get_statuses())
        results = sorted(self._session.results.get_results_for_run(old_run_id, status_id=statuses),
                         key=lambda result: result.created_on, reverse=False)
        if old_tests is None:
            old_tests = self._session.tests.get_tests(old_run_id)

        new_tests = self._session.tests.get_tests(new_run_id)
        result_to_delete = []
        for result in results:
            delete_result = False
            test_in_old_tests = next(filter(lambda x: x.id == result.test_id, old_tests), None)
            if test_in_old_tests is not None:
                test_in_new_tests = next(filter(lambda x: x.case_id == test_in_old_tests.case_id, new_tests), None)
                if test_in_new_tests is not None:
                    if overwrite_results is not None:
                        copy_results = True if test_in_new_tests.status_id in overwrite_results else False
                    else:
                        copy_results = True
                    if copy_results is True:
                        result.test_id = test_in_new_tests.id
                    else:
                        delete_result = True
                else:
                    delete_result = True
            else:
                delete_result = True
            if delete_result:
                result_to_delete.append(result)

        for result in result_to_delete:
            results.remove(result)

        return self._session.results.add_results(new_run_id, to_json(results))

    def delete_cases_by_regex(self, string_with_cases_ids: str) -> str:
        """
        Delete cases from TestRail using regEx for take id from text
        """
        case_ids, deleted_count = re.findall(r'\d+', string_with_cases_ids), 0
        for case_id in case_ids:
            if self._session.cases.delete_case(int(case_id)) == 200:
                deleted_count += 1
        return f'Deleted {deleted_count} of {len(case_ids)}'

    def get_plan_id_by_name(self, plan_name: str) -> Plan:
        return next(tuple(filter(lambda plan: plan.name == plan_name, self._session.plans.get_plans())), None)

    def add_link_to_test_rail_in_allure(self, run_id: int, allure_results_path: str):
        tests = [(x.id, trim(x.title)) for x in self._session.tests.get_tests(run_id)]

        for report in filter(lambda allure: allure.split('.')[-1] == 'json', os.listdir(allure_results_path)):
            path = os.path.join(allure_results_path, report)
            text = json.loads(open(path, 'r').read())
            params = re.findall(r'(<\S+>)', text['name'])
            if params:
                for params in text['parameters']:
                    text['name'] = text['name'].replace(f"<{params['name']}>", params['value'])
                text['name'] = trim(re.sub(r'\[.*]', '', text['name']))
            result = tuple(filter(lambda x: x[1] == text['name'], tests))
            if len(result) > 0:
                href = '<br><a href ="{url}" target="_blank">Link to Test Rail result</a>'. \
                    format(url=f"{self._session.result_url}/{result[0][0]}")
                if text.get('descriptionHtml'):
                    text['descriptionHtml'] += href
                else:
                    text['descriptionHtml'] = href
                open(path, 'w').write(json.dumps(text))

    def get_run_by_config(self, plan_id: int, config: str, suite_name: int):
        configuration = sort_configurations(config, self._session)
        plan = self._session.plans.get_plan(plan_id)
        for entry in plan.entries:
            for run in entry.runs:
                if run.name == suite_name and run.config == configuration:
                    return run.id
        raise Exception(f"Can't find run by config {config} in plan {plan_id}")

    def _delete_extra_cases_from_test_rail(self, features_path: str, return_cases: bool, suite_name: str):
        """
        Deleting from Test Rail App cases, that doesn't find in features
        """
        feature_files = self.get_all_feature_file(features_path)
        features_tags = tuple(chain.from_iterable((re.findall(fr'{TR_PREFIX}\d+', open(feature, 'r').read())
                                                   for feature in feature_files)))
        feature_ids = [int(y.replace(TR_PREFIX, '')) for y in features_tags]
        suiteid = tuple(filter(lambda suite: suite.name == suite_name, self._session.suites.get_suites()))[0]['id']
        cases = self._session.cases.get_cases(suite_id=suiteid)
        cases_ids = [int(y.id) for y in cases]
        if return_cases:
            return list(filter(lambda y: y.id not in feature_ids, cases))
        extra_id = list(filter(lambda y: y not in feature_ids, cases_ids))
        with open('extra_tests.txt', 'w') as file:
            file.write('\n'.join([x for x in extra_id]))

    @staticmethod
    def get_all_feature_file(features_path):
        return [f"{root}/{file}" for root, dirs, files in os.walk(features_path, topdown=False)
                for file in files if file.split('.')[-1] == 'feature']
