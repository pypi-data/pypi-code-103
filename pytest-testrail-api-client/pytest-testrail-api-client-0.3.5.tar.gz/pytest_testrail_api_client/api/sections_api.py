from typing import List

import pytest_testrail_api_client.modules.category as category
from pytest_testrail_api_client.modules.classes import Section
import pytest_testrail_api_client.service as service


class SectionsApi(category.Base):
    __sub_host = '/api/v2'

    def get_section(self, section_id: int) -> Section:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#getsection

        Returns an existing section
        :param section_id: The ID of the section
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_section/{section_id}'), Section)

    def get_sections(self, suite_id: int = None, project_id: int = None) -> List[Section]:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#getsections

        Returns a list of sections for a project and test suite
        :param suite_id: The ID of the test suite (optional if the project is operating in single suite mode)
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :return:
        """
        params = {}
        if project_id is None:
            project_id = self._session.project_id
        if suite_id is not None:
            params = {'suite_id': suite_id}
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_sections/{project_id}', params=params),
                           Section)

    def add_section(self, name: str, project_id: int = None, description: str = None, suite_id: int = None,
                    parent_id: int = None) -> Section:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#addsection

        Creates a new section
        :param name: The name of the section (required)
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :param description: The description of the section
        :param suite_id: The ID of the test suite (ignored if the project is operating in
                            single suite mode, required otherwise)
        :param parent_id: The ID of the parent section (to build section hierarchies)
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        data = service.get_dict_from_locals(locals(), exclude=['project_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_section/{project_id}', data=data),
                           Section)

    def move_section(self, section_id: int, parent_id: int = None, after_id: int = None) -> Section:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#movesection

        Moves a section to another suite or section. (Requires TestRail 6.5.2 or later)
        :param section_id: The ID of the section
        :param parent_id: The ID of the parent section (it can be null if it should be moved to the root).
                            Must be in the same project and suite. May not be direct child of the section being moved.
        :param after_id: The section ID after which the section should be put (can be null)
        :return:
        """
        data = service.get_dict_from_locals(locals(), exclude=['section_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/move_section/{section_id}', data=data),
                           Section)

    def update_section(self, section_id: int, name: str = None, description: str = None) -> Section:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#updatesection

        Updates an existing section (partial updates are supported, i.e. you can submit and update
        specific fields only).
        :param section_id: The ID of the section
        :param name: The name of the section
        :param description: The description of the section
        :return:
        """
        data = service.get_dict_from_locals(locals(), exclude=['section_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/update_section/{section_id}', data=data),
                           Section)

    def delete_section(self, section_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/sections#deletesection

        Deletes an existing section
        :param section_id: The ID of the section
        :return: status code
        """
        return self._session.request('post', f'{self.__sub_host}/delete_section/{section_id}',
                                     return_type='status_code')
