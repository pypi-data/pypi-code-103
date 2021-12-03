from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.service import get_dict_from_locals


class SuitesApi(Base):
    __sub_host = '/api/v2'

    def get_suite(self, suite_id: int) -> Suite:
        """
        https://www.gurock.com/testrail/docs/api/reference/suites#getsuite

        Returns an existing test suite
        :param suite_id: The ID of the test suite
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_suite/{suite_id}'), Suite)

    def get_suites(self, project_id: int = None) -> List[Suite]:
        """
        https://www.gurock.com/testrail/docs/api/reference/suites#getsuites

        Returns a list of test suites for a project
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :return: List[Suite]
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_suites/{project_id}'), Suite)

    def add_suite(self, name: str, project_id: int = None, description: str = None) -> Suite:
        """
        https://www.gurock.com/testrail/docs/api/reference/suites#addsuite

        Creates a new test suite.
        :param name: The name of the test suite (required)
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :param description: The description of the test suite
        :return: Suite
        """
        if project_id is None:
            project_id = self._session.project_id
        data = get_dict_from_locals(locals(), exclude=['project_id'])
        return self._valid(self._session.request('get', f'{self.__sub_host}/add_suite/{project_id}', data=data), Suite)

    def update_suite(self, suite_id: int, name: str = None, description: str = None) -> Suite:
        """
        https://www.gurock.com/testrail/docs/api/reference/suites#addsuite

        Creates a new test suite.
        :param suite_id: The ID of the test suite
        :param name: The name of the test suite (required)
        :param description: The description of the test suite
        :return: Suite
        """
        data = get_dict_from_locals(locals(), exclude=['suite_id'])
        if len(data.items()) == 0:
            raise ValueError('Missing any update for suite')
        else:
            return self._valid(self._session.request('get', f'{self.__sub_host}/update_suite/{suite_id}', data=data),
                               Suite)

    def delete_suite(self, suite_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/suites#deletesuite

        Deletes an existing test suite
        :param suite_id: The ID of the test suite
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_suite/{suite_id}', return_type='status_code')
