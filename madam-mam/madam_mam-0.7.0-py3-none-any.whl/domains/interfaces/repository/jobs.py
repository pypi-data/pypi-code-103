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
import uuid
from typing import List, Optional

from madam.domains.entities.job import Job


class JobRepositoryInterface(abc.ABC):
    """
    JobRepositoryInterface class
    """

    @abc.abstractmethod
    def create(self, job: Job) -> None:
        """
        Create a new job entry

        :param job: Job instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, id: uuid.UUID) -> Job:  # pylint: disable=redefined-builtin
        """
        Get a Job object by its ID

        :param id: ID of the Job
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, id: uuid.UUID, **kwargs):  # pylint: disable=redefined-builtin
        """
        Update fields of job from key=value arguments

        :param id: Job ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete Job entry

        :param id: Job ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: Optional[str] = None,
        workflow_instance_id: Optional[uuid.UUID] = None,
    ) -> List[Job]:
        """
        Return a list of Job objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="start_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param status: Status constant to filter by, None for all status (default=None)
        :param workflow_instance_id: Parent workflow instance ID to filter by, None for all jobs (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, status: str = None, instance_id: Optional[uuid.UUID] = None) -> int:
        """
        Return total count of jobs

        :param status: Filter by status (default=None)
        :param instance_id: Filter by parent WorkflowInstance ID (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_by_workflow_instance_id(
        self, id, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        """
        Update fields of all job entries with parent workflow instance id

        :param id: WorkflowInstance ID
        :param kwargs: Fields to update
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_ids_by_workflow_instance_id(
        self, id  # pylint: disable=redefined-builtin
    ) -> List[uuid.UUID]:
        """
        Get all job ids with parent workflow instance id

        :param id: WorkflowInstance ID
        :return:
        """
        raise NotImplementedError
