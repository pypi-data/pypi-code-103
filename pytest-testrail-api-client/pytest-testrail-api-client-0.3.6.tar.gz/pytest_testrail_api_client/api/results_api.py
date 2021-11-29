from datetime import datetime
from itertools import chain
from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.result import Result
from pytest_testrail_api_client.service import split_by_coma, get_dict_from_locals, validate_id, validate_variable, \
    split_list


class ResultsApi(Base):
    __sub_host = '/api/v2'

    def get_results(self, test_id: int) -> List[Result]:
        """
        https://www.gurock.com/testrail/docs/api/reference/results#getresults

        Returns a list of test results for a test
        :param test_id: The ID of the test
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_results/{test_id}'), Result,
                           add_session=True)

    def get_results_for_case(self, run_id: int, case_id: int, defects_filter: str = None,
                             status_id: (str, list) = None) -> List[Result]:
        """
        https://www.gurock.com/testrail/docs/api/reference/results#getresultsforcase

        Returns a list of test results for a test run and case combination
        :param run_id: The ID of the test run
        :param case_id: The ID of the test case
        :param defects_filter: A single Defect ID (e.g. TR-1, 4291, etc.)
        :param status_id: A comma-separated list of status IDs to filter by
        :return:
        """
        status_id = validate_id(status_id)
        params = get_dict_from_locals(locals(), exclude=['run_id', 'case_id'])
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_results_for_case/{run_id}/{case_id}',
                                                 params=params), Result, add_session=True)

    def get_results_for_run(self, run_id: int, created_after: datetime = None, created_before: datetime = None,
                            created_by: (int, list) = None, defects_filter: str = None,
                            status_id: (str, list) = None) -> List[Result]:
        """
        https://www.gurock.com/testrail/docs/api/reference/results#getresultsforrun

        Returns a list of test results for a test run
        :param run_id: The ID of the test run
        :param created_after: Only return test results created after this date
        :param created_before: Only return test results created before this date
        :param created_by: A comma-separated list of creators (user IDs) to filter by
        :param defects_filter: A single Defect ID (e.g. TR-1, 4291, etc.)
        :param status_id: A comma-separated list of status IDs to filter by
        :return:
        """
        if created_after is not None:
            created_after = int(created_after.timestamp())
        if created_before is not None:
            created_before = int(created_before.timestamp())
        created_by = split_by_coma(created_by)
        status_id = validate_id(status_id)
        params = get_dict_from_locals(locals(), exclude=['run_id'])
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_results_for_run/{run_id}',
                                                 params=params), Result, add_session=True)

    def add_result(self, test_id: int, status_id: int = None, comment: str = None, version: str = None,
                   elapsed: str = None, defects: str = None, assignedto_id: int = None,
                   custom_step_results: list = None, **kwargs):
        """
        https://www.gurock.com/testrail/docs/api/reference/results#addresult

        Adds a new test result, comment or assigns a test.
        It’s recommended to use add_results instead if you plan to add results for multiple tests.
        :param test_id: The ID of the test the result should be added to
        :param status_id: The ID of the test status
        :param comment: The comment / description for the test result
        :param version: The version or build you tested against
        :param elapsed: The time it took to execute the test, e.g. “30s” or “1m 45s”
        :param defects: A comma-separated list of defects to link to the test result
        :param assignedto_id: The ID of a user the test should be assigned to
        :param custom_step_results: BDD steps description
        :param kwargs: Custom fields
        :return:
        """
        defects = split_by_coma(defects)
        data = get_dict_from_locals(locals(), exclude=['test_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_result/{test_id}', data=data), Result,
                           add_session=True)

    def add_result_for_case(self, run_id: int, case_id: int, status_id: int = None, comment: str = None,
                            version: str = None, elapsed: str = None, defects: str = None, assignedto_id: int = None,
                            custom_step_results: list = None, **kwargs):
        """
        https://www.gurock.com/testrail/docs/api/reference/results#addresultforcase

        Adds a new test result, comment or assigns a test (for a test run and case combination).
        It’s recommended to use add_results_for_cases instead if you plan to add results for multiple test cases.
        :param run_id: The ID of the test run
        :param case_id: The ID of the test case
        :param status_id: The ID of the test status
        :param comment: The comment / description for the test result
        :param version: The version or build you tested against
        :param elapsed: The time it took to execute the test, e.g. “30s” or “1m 45s”
        :param defects: A comma-separated list of defects to link to the test result
        :param assignedto_id: The ID of a user the test should be assigned to
        :param custom_step_results: BDD steps description
        :param kwargs: Custom fields
        :return:
        """
        defects = split_by_coma(defects)
        data = get_dict_from_locals(locals(), exclude=['test_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_result_for_case/{run_id}/{case_id}',
                                                 data=data), Result, add_session=True)

    def add_results(self, run_id: int, results: (list, tuple)) -> List[Result]:
        """
        https://www.gurock.com/testrail/docs/api/reference/results#addresults

        Adds one or more new test results, comments or assigns one or more tests.
        Ideal for test automation to bulk-add multiple test results in one step
        :param run_id: The ID of the test run the results should be added to.
                        Please note that all referenced tests must belong to the same test run.
        :param results:
        :return: List[Result]
        """
        validate_variable(results, (list, tuple), 'results')
        validate_variable(run_id, int, 'run_id')
        return self.__send_results(results, run_id, for_case=False)

    def add_results_for_cases(self, run_id: int, results: (list, tuple)) -> List[Result]:
        """
        https://www.gurock.com/testrail/docs/api/reference/results#addresultsforcases

        Adds one or more new test results, comments or assigns one or more tests (using the case IDs).
        Ideal for test automation to bulk-add multiple test results in one step.
        :param run_id: The ID of the test run the results should be added to.
                        Please note that all referenced tests must belong to the same test run.
        :param results:
        :return: List[Result]
        """
        validate_variable(results, (list, tuple), 'results')
        validate_variable(run_id, int, 'run_id')
        return self.__send_results(results, run_id, for_case=True)

    def __send_results(self, results, run_id: int, for_case: bool = False):
        url = 'add_results_for_cases' if for_case else 'add_results'
        if len(results) > 1000:
            result = []
            for sub_result in split_list(results, separator=1000):
                data = {'results': sub_result}
                result.append(
                    self._valid(self._session.request('post', f'{self.__sub_host}/{url}/{run_id}', data=data), Result,
                                add_session=True))
            return tuple(chain.from_iterable(result))

        else:
            data = {'results': results}
            return self._valid(self._session.request('post', f'{self.__sub_host}/{url}/{run_id}', data=data),
                               Result, add_session=True)
