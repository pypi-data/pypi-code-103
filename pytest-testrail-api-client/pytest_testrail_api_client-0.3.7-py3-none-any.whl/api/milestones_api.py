from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Milestone
from pytest_testrail_api_client.service import get_dict_from_locals


class MilestonesApi(Base):
    __sub_host = '/api/v2'

    def get_milestone(self, milestone_id: int) -> Milestone:
        """
        https://www.gurock.com/testrail/docs/api/reference/milestones#getmilestone

        Returns an existing milestone
        :param milestone_id: The ID of the milestone
        :return: Milestone object
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_milestone/{milestone_id}'), Milestone)

    def get_milestones(self, project_id: int = None) -> List[Milestone]:
        """
        https://www.gurock.com/testrail/docs/api/reference/milestones#getmilestones

        Returns the list of milestones for a project
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :return: List[Milestone]
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_milestones/{project_id}'), Milestone)

    def add_milestone(self, name: str, project_id: int = None, description: str = None, due_on=None,
                      parent_id: int = None, refs: str = None, start_on=None) -> Milestone:
        """
        https://www.gurock.com/testrail/docs/api/reference/milestones#addmilestone

        Creates a new milestone
        :param name: The name of the milestone (required)
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :param description: The description of the milestone
        :param due_on: The due date of the milestone (as UNIX timestamp)
        :param parent_id: The ID of the parent milestone, if any (for sub-milestones) (available since TestRail 5.3)
        :param refs: A comma-separated list of references/requirements (available since TestRail 6.4)
        :param start_on: The scheduled start date of the milestone (as UNIX timestamp) (available since TestRail 5.3)
        :return: Milestone
        """
        if project_id is None:
            project_id = self._session.project_id
        data = get_dict_from_locals(locals(), exclude=['project_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_milestone/{project_id}', data=data),
                           Milestone)

    def update_milestone(self, milestone_id: int, is_completed: bool = None, is_started: bool = None,
                         parent_id: int = None, start_on=None) -> Milestone:
        """
        https://www.gurock.com/testrail/docs/api/reference/milestones#updatemilestone

        Updates an existing milestone (partial updates are supported, i.e. you can submit and update
        specific fields only)
        :param milestone_id: The ID of the milestone
        :param is_completed: True if a milestone is considered completed and false otherwise
        :param is_started: True if a milestone is considered started and false otherwise
        :param parent_id: The ID of the parent milestone, if any (for sub-milestones) (available since TestRail 5.3)
        :param start_on: The scheduled start date of the milestone (as UNIX timestamp) (available since TestRail 5.3)
        :return: Milestone
        """
        data = get_dict_from_locals(locals(), exclude=['milestone_id'])
        return self._valid(
            self._session.request('post', f'{self.__sub_host}/update_milestone/{milestone_id}', data=data), Milestone)

    def delete_milestone(self, milestone_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/milestones#deletemilestone

        Deletes an existing milestone
        :param milestone_id: The ID of the milestone
        :return: status code
        """
        return self._session.request('post', f'{self.__sub_host}/delete_milestone/{milestone_id}',
                                     return_type='status_code')
