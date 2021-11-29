from typing import List

from pytest_testrail_api_client.modules.case import Case, CaseHistory
from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.service import get_dict_from_locals, validate_id


class CasesApi(Base):
    __sub_host = '/api/v2'

    def get_case(self, case_id: int) -> Case:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#getcase

        Returns an existing test case
        :param case_id: The ID of the test case
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_case/{case_id}'), Case)

    def get_cases(self, project_id: int = None, suite_id: int = None) -> List[Case]:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#getcases

        Returns a list of test cases for a project or specific test suite (if the project has multiple suites enabled)
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :param suite_id: The ID of the test suite (optional if the project is operating in single suite mode)
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        params = {}
        if suite_id:
            params.update({'suite_id': suite_id})
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_cases/{project_id}', params=params),
                           Case)

    def get_history_for_case(self, case_id: int) -> CaseHistory:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#gethistoryforcase

        Returns the edit history for a test case_id. Requires TestRail 6.5.4 or later.
        :param case_id: The ID of the test case
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_history_for_case/{case_id}'),
                           CaseHistory)

    def add_case(self, section_id: int, title: str, template_id: int = None, type_id: int = None,
                 priority_id: int = None, estimate=None, milestone_id: int = None, refs: str = None, **kwargs) -> Case:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#addcase

        Creates a new test case
        :param section_id: The ID of the section the test case should be added to
        :param title: The title of the test case (required)
        :param template_id: The ID of the template (field layout) (requires TestRail 5.2 or later)
        :param type_id: The ID of the case type
        :param priority_id: The ID of the case priority
        :param estimate: The estimate, e.g. “30s” or “1m 45s”
        :param milestone_id: The ID of the milestone to link to the test case
        :param refs: A comma-separated list of references/requirements
        :return:
        """
        data = get_dict_from_locals(locals(), exclude=['section_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_case/{section_id}', data=data), Case)

    def copy_cases_to_section(self, section_id: int, case_ids: (list, str)) -> Case:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#copycasestosection

        Copies the list of cases to another suite/section.
        :param section_id: The ID of the section the test case should be copied to
        :param case_ids: A comma-separated list of case IDs
        :return:
        """
        if isinstance(case_ids, str):
            case_ids = case_ids.replace(' ', '').split(',')
        data = {'case_ids': case_ids}
        return self._valid(
            self._session.request('post', f'{self.__sub_host}/copy_cases_to_section/{section_id}', data=data), Case)

    def update_case(self, case_id: int, section_id: int = None, title: str = None, template_id: int = None,
                    type_id: int = None, priority_id: int = None, estimate=None, milestone_id: int = None,
                    refs: str = None, **kwargs) -> Case:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#updatecase

        Updates an existing test case
        (partial updates are supported, i.e. you can submit and update specific fields only).
        :param case_id: The ID of the test case
        :param section_id: The ID of the section the test case should be added to
        :param title: The title of the test case (required)
        :param template_id: The ID of the template (field layout) (requires TestRail 5.2 or later)
        :param type_id: The ID of the case type
        :param priority_id: The ID of the case priority
        :param estimate: The estimate, e.g. “30s” or “1m 45s”
        :param milestone_id: The ID of the milestone to link to the test case
        :param refs: A comma-separated list of references/requirements
        :param kwargs: Custom fields
        :return:
        """
        data = get_dict_from_locals(locals(), exclude=['case_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/update_case/{case_id}', data=data), Case)

    def update_cases(self, suite_id: int, cases_ids: (tuple, list), title: str = None, template_id: int = None,
                     type_id: int = None, priority_id: int = None, estimate=None, milestone_id: int = None,
                     refs: str = None, **kwargs) -> List[Case]:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#updatecases

        Updates multiple test cases with the same values, such as setting a set of test cases to High priority.
        This does not support updating multiple test cases with different values per test case.
        :param suite_id: The ID of the suite which contains the test cases to be updated
        :param cases_ids: List of cases id for update
        :param title: The title of the test case (required)
        :param template_id: The ID of the template (field layout) (requires TestRail 5.2 or later)
        :param type_id: The ID of the case type
        :param priority_id: The ID of the case priority
        :param estimate: The estimate, e.g. “30s” or “1m 45s”
        :param milestone_id: The ID of the milestone to link to the test case
        :param refs: A comma-separated list of references/requirements
        :param kwargs: Custom fields
        :return:
        """
        data = get_dict_from_locals(locals(), exclude=['suite_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/update_cases/{suite_id}', data=data), Case)

    def move_cases_to_section(self, section_id: int = None, suite_id: int = None,
                              case_ids: (tuple, list) = None) -> List[Case]:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#movecasestosection

        Moves cases to another suite or section.
        :param section_id: The ID of the section the case will be moved to.
        :param suite_id: The ID of the suite the case will be moved to.
        :param case_ids: A comma-separated list of case IDs
        :return:
        """
        case_ids = validate_id(case_ids)
        params = get_dict_from_locals(locals())
        return self._valid(self._session.request('post', f'{self.__sub_host}/move_cases_to_section', params=params),
                           Case)

    def delete_case(self, case_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#deletecase

        Deletes an existing test case
        :param case_id: The ID of the test case
        :return: status code
        """
        return self._session.request('post', f'{self.__sub_host}/delete_case/{case_id}', return_type='status_code')

    def delete_cases(self, case_ids: (list, str) = None, project_id: int = None, suite_id: int = None) -> List[Case]:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases#deletecases

        Deletes multiple test cases from a project or test suite
        :param case_ids:
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :param suite_id: The ID of the suite (Only required if project is in multi-suite mode)
        :return:
        """
        params, data = get_dict_from_locals(locals(), exclude=['case_ids', 'project_id']), {}
        if case_ids is not None:
            if isinstance(case_ids, str):
                case_ids = case_ids.replace(' ', '').split(',')
            data = {'case_ids': case_ids}
        if project_id is None:
            project_id = self._session.project_id
        params.update({'soft': 1})
        return self._valid(self._session.request('post', f'{self.__sub_host}/delete_cases/{project_id}',
                                                 data=data, params=params), Case)
