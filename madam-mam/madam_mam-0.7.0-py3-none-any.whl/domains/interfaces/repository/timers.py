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

from madam.domains.entities.timer import CyclicTimer, DateTimer
from madam.domains.entities.workflow import Workflow


class TimerRepositoryInterface(abc.ABC):
    """
    TimerRepositoryInterface class
    """

    @abc.abstractmethod
    def create_date_timer(self, timer: DateTimer) -> None:
        """
        Create a new date timer entry

        :param timer: DateTimer instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_cyclic_timer(self, timer: CyclicTimer) -> None:
        """
        Create a new cyclic timer entry

        :param timer: CyclicTimer instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(
        self, id: uuid.UUID  # pylint: disable=redefined-builtin
    ) -> Union[DateTimer, CyclicTimer]:
        """
        Get a Timer object by its ID

        :param id: ID of the timer
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self, id: uuid.UUID, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        """
        Update kwargs fields of timer entry

        :param id: ID of timer
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete timer entry

        :param id: ID of timer
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
    ) -> List[Union[DateTimer, CyclicTimer]]:
        """
        Return a list of Timer objects

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
        Return total count of Timer instances

        :param status: Filter by status (default=None)
        :param workflow: Filter by parent Workflow (default=None)
        :return:
        """
        raise NotImplementedError
