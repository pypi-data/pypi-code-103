# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

import abc
from typing import List, Optional

from madam.domains.entities.workflow import Workflow


class WorkflowRepositoryInterface(abc.ABC):
    """
    WorkflowRepositoryInterface class
    """

    @abc.abstractmethod
    def create(self, workflow: Workflow) -> None:
        """
        Create a new workflow entry

        :param workflow: Workflow object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(
        self,
        id: str,  # pylint: disable=redefined-builtin
        version: Optional[int] = None,
    ) -> Workflow:
        """
        Get a Workflow object by its id and version.
        If version is None, the last version is returned.

        :param id: Id of the workflow
        :param version: Version number
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: str) -> None:  # pylint: disable=redefined-builtin
        """

        Delete all versions of workflow ID with children (timers, workflow_instances)

        :param id: Workflow ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_version_by_id(
        self, id: str  # pylint: disable=redefined-builtin
    ) -> int:
        """
        Get last version of workflow by ID

        :param id: Workflow's ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "created_at",
        sort_ascending: bool = True,
        last_version: bool = False,
    ) -> List[Workflow]:
        """
        Return a list of Workflow objects paginated, filtered and sorted

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="created_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param last_version: Only last version for each workflow (default=False)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, last_version: bool = False) -> int:
        """
        Return total number of workflows

        :param last_version: Filter to get only last_version if True (default=False)
        :return:
        """
        raise NotImplementedError
