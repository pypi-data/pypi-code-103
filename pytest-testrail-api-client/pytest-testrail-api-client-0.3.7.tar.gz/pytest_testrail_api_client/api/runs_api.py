from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.plan import Run
from pytest_testrail_api_client.service import split_by_coma, get_dict_from_locals


class RunsApi(Base):
    __sub_host = '/api/v2'

    def get_run(self, run_id: int) -> Run:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#getrun

        Returns an existing test run
        :param run_id: The ID of the test run
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_run/{run_id}'), Run)

    def get_runs(self, project_id: int = None) -> List[Run]:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#getruns

        Returns a list of test runs for a project
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_runs/{project_id}'), Run)

    def add_run(self, suite_id: int = None, name: str = None, description: str = None, milestone_id: int = None,
                assignedto_id: int = None, include_all: bool = None, case_ids: (str, list) = None,
                refs: str = None, project_id: int = None) -> Run:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#addrun

        Creates a new test run
        :param suite_id: The ID of the test suite for the test run
                        (optional if the project is operating in single suite mode, required otherwise)
        :param name: The name of the test run
        :param description: The description of the test run
        :param milestone_id: The ID of the milestone to link to the test run
        :param assignedto_id: The ID of the user the test run should be assigned to
        :param include_all: True for including all test cases of the test suite and false for a custom case selection
                            (default: true)
        :param case_ids: An array of case IDs for the custom case selection
        :param refs: A comma-separated list of references/requirements (Requires TestRail 6.1 or later)
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        case_ids = split_by_coma(case_ids)
        data = get_dict_from_locals(locals(), exclude=['project_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_run/{project_id}'), Run)

    def update_run(self, run_id: int, name: str = None, description: str = None, milestone_id: int = None,
                   include_all: bool = None, case_ids: (str, list) = None, refs: str = None) -> Run:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#updaterun

        Updates an existing test run
        (partial updates are supported, i.e. you can submit and update specific fields only).
        :param run_id: The ID of the test run
        :param name: The name of the test run
        :param description: The description of the test run
        :param milestone_id: The ID of the milestone to link to the test run
        :param include_all: True for including all test cases of the test suite and false for a custom case selection
        :param case_ids: An array of case IDs for the custom case selection
        :param refs: A comma-separated list of references/requirements (Requires TestRail 6.1 or later)
        :return:
        """
        case_ids = split_by_coma(case_ids)
        data = get_dict_from_locals(locals())
        return self._valid(self._session.request('post', f'{self.__sub_host}/update_run/{run_id}'), Run)

    def close_run(self, run_id: int) -> Run:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#closerun

        Closes an existing test run and archives its tests & results
        :param run_id: The ID of the test run
        :return:
        """
        return self._valid(self._session.request('post', f'{self.__sub_host}/close_run/{run_id}'), Run)

    def delete_run(self, run_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/runs#deleterun

        Deletes an existing test run
        :param run_id: The ID of the test run
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_run/{run_id}', return_type='status_code')
