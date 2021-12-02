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
from typing import List, Optional, Union

from madam.domains.entities.application import Application
from madam.domains.entities.job import Job
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import WorkflowInstance


class ApplicationRepositoryInterface(abc.ABC):
    """
    ApplicationRepositoryInterface class
    """

    @abc.abstractmethod
    def create(self, application: Application) -> None:
        """
        Create a new application entry

        :param application: Application instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, id: uuid.UUID) -> Application:  # pylint: disable=redefined-builtin
        """
        Get an Application object by its ID

        :param id: ID of the Application
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self, id: uuid.UUID, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        """
        Update fields of Application ID from key=value arguments

        :param id: Application ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete application from database and his container if any

        :param id: Application ID
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
        status: str = None,
        job_id: Optional[uuid.UUID] = None,
    ) -> List[Application]:
        """
        Return a list of job Application objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="start_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param status: Status constant to filter by, None for all status (default=None)
        :param job_id: Parent job ID to filter by, None for all applications (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, status: str = None, job_id: Optional[uuid.UUID] = None) -> int:
        """
        Return total count of applications

        :param status: Filter by status (default=None)
        :param job_id: Filter by parent Job ID (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_container_ids_by_parent(
        self, parent: Union[Workflow, WorkflowInstance, Job, Application]
    ) -> List[str]:
        """
        Get all container IDs created from the parent provided

        :param parent: Workflow, WorkflowInstance, Job or Application object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_by_job_ids(self, ids: List[uuid.UUID], **kwargs) -> None:
        """
        Update all applications with job ids as parent

        :param ids: List of job ids
        :return:
        """
        raise NotImplementedError
