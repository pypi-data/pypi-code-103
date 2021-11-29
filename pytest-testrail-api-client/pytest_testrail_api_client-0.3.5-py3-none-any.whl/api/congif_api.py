from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.config_obj import Config


class ConfigsApi(Base):
    __sub_host = '/api/v2'

    def get_configs(self, project_id: int = None) -> List[Config]:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#getconfigs

        Returns a list of available configurations, grouped by configuration groups
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :return: List[Config]
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_configs/{project_id}'), Config)

    def add_config_group(self, name: str, project_id: int = None) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#addconfiggroup

        Creates a new configuration group (requires TestRail 5.2 or later).
        :param name: The name of the configuration group (required)
        :param project_id: The ID of the project the configuration group should be added to.
                            If not indicated - takes default project_id
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        data = {'name': name}
        return self._session.request('post', f'{self.__sub_host}/add_config_group/{project_id}', data=data,
                                     return_type='status_code')

    def add_config(self, config_group_id: int, name: str) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#addconfig

        Creates a new configuration (requires TestRail 5.2 or later)
        :param config_group_id: The ID of the configuration group the configuration should be added to
        :param name: The name of the configuration (required)
        :return:
        """
        data = {'name': name}
        return self._session.request('post', f'{self.__sub_host}/add_config/{config_group_id}', data=data,
                                     return_type='status_code')

    def update_config_group(self, config_group_id: int, name: str) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#updateconfiggroup

        Updates an existing configuration group (requires TestRail 5.2 or later)
        :param config_group_id: The ID of the configuration group
        :param name: The name of the configuration group
        :return:
        """
        data = {'name': name}
        return self._session.request('post', f'{self.__sub_host}/update_config_group/{config_group_id}', data=data,
                                     return_type='status_code')

    def update_config(self, config_id: int, name: str) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#updateconfig

        Updates an existing configuration (requires TestRail 5.2 or later).
        :param config_id: The ID of the configuration
        :param name: The name of the configuration
        :return:
        """
        data = {'name': name}
        return self._session.request('post', f'{self.__sub_host}/update_config/{config_id}', data=data,
                                     return_type='status_code')

    def delete_config_group(self, config_group_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#deleteconfiggroup

        Deletes an existing configuration group and its configurations (requires TestRail 5.2 or later)
        :param config_group_id: The ID of the configuration group
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_config_group/{config_group_id}',
                                     return_type='status_code')

    def delete_config(self, config_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/configurations#deleteconfig

        Deletes an existing configuration (requires TestRail 5.2 or later)
        :param config_id: The ID of the configuration
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_config/{config_id}',
                                     return_type='status_code')
