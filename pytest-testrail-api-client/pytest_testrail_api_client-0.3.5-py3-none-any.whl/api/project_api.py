from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Project
from pytest_testrail_api_client.service import get_dict_from_locals


class ProjectApi(Base):
    __sub_host = '/api/v2'

    def get_project(self, project_id: int) -> Project:
        """
        https://www.gurock.com/testrail/docs/api/reference/projects#getproject

        Returns an existing project
        :param project_id: The ID of the project
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_project/{project_id}'), Project)

    def get_projects(self) -> List[Project]:
        """
        https://www.gurock.com/testrail/docs/api/reference/projects#getprojects

        Returns the list of available projects
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_projects'), Project)

    def add_project(self, name: str, announcement: str = None, show_announcement: bool = True,
                    suite_mode: int = None) -> Project:
        """
        https://www.gurock.com/testrail/docs/api/reference/projects#addproject

        Creates a new project (admin status required)
        :param name: The name of the project (required)
        :param announcement: The description of the project
        :param show_announcement: True if the announcement should be displayed on the project’s
                                    overview page and false otherwise
        :param suite_mode: The suite mode of the project
                            (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        :return:
        """
        data = get_dict_from_locals(locals())
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_project', data=data), Project)

    def update_project(self, project_id: int, name: str = None, announcement: str = None,
                       show_announcement: bool = None, is_completed: bool = None) -> Project:
        """
        https://www.gurock.com/testrail/docs/api/reference/projects#updateproject

        Updates an existing project (admin status required; partial updates are supported,
                i.e. you can submit and update specific fields only).
        :param project_id: The ID of the project
        :param name: The name of the project
        :param announcement: The description of the project
        :param show_announcement: True if the annoucnement should be displayed on
                                    the project’s overview page and false otherwise
        :param is_completed: Specifies whether a project is considered completed or not
        :return: Project
        """
        data = get_dict_from_locals(locals())
        return self._valid(self._session.request('post', f'{self.__sub_host}/update_project/{project_id}', data=data),
                           Project)

    def delete_project(self, project_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/projects#deleteproject

        Deletes an existing project (admin status required)
        :param project_id: The ID of the project
        :return: int
        """
        return self._session.request('post', f'{self.__sub_host}/delete_project/{project_id}',
                                     return_type='status_code')
