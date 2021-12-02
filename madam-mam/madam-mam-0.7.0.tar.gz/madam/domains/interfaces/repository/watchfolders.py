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

from madam.domains.entities.watchfolder import Watchfolder
from madam.domains.entities.workflow import Workflow


class WatchfolderRepositoryInterface(abc.ABC):
    """
    WatchfolderRepositoryInterface class
    """

    @abc.abstractmethod
    def create(self, watchfolder: Watchfolder) -> None:
        """
        Create a new watchfolder entry

        :param watchfolder: Watchfolder to create
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, id: uuid.UUID) -> Watchfolder:  # pylint: disable=redefined-builtin
        """
        Get a Watchfolder object by its ID

        :param id: ID of the watchfolder
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self, id: uuid.UUID, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        """
        Update kwargs fields of watchfolder entry

        :param id: ID of watchfolder
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete watchfolder entry

        :param id: ID of watchfolder
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
        workflow: Optional[Workflow] = None,
    ) -> List[Watchfolder]:
        """
        Return a list of Watchfolder objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="start_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param status: Status constant to filter by, None for all status (default=None)
        :param workflow: Parent workflow to filter by (default=None)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, status: str = None, workflow: Workflow = None) -> int:
        """
        Return total count of Watchfolder instances

        :param status: Filter by status (default=None)
        :param workflow: Filter by parent Workflow (default=None)
        :return:
        """
        raise NotImplementedError
