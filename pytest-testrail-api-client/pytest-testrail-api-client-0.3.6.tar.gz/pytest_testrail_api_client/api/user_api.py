from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import User


class UsersApi(Base):
    __sub_host = '/api/v2'

    def get_user(self, user_id: int) -> User:
        """
        https://www.gurock.com/testrail/docs/api/reference/users#getuser

        Returns an existing user.
        :param user_id: The ID of the user
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_user/{user_id}'), User)

    def get_current_user(self) -> List[User]:
        """
        https://www.gurock.com/testrail/docs/api/reference/users#getcurrentuser

        Returns user details for the TestRail user making the API request (Requires TestRail 6.6 or later)
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_current_user'), User)

    def get_user_by_email(self, email: str) -> User:
        """
        https://www.gurock.com/testrail/docs/api/reference/users#getuserbyemail

        Returns an existing user by his/her email address.
        :param email: The email address to get the user for
        :return:
        """
        param = {'email': email}
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_user_by_email', params=param), User)

    def get_users(self, project_id: int = None) -> List[User]:
        """
        https://www.gurock.com/testrail/docs/api/reference/users#getusers

        Returns a list of users
        :param project_id: The ID of the project for which you would like to retrieve user information.
                            (Required for non-administrators. Requires TestRail 6.6 or later.)
                            If project_id is None - takes default project_id
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_users/{project_id}'), User)
