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

import uuid
from functools import reduce
from typing import List, Optional, Union

from sql import Column, Table
from sql.aggregate import Count

from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.domains.entities.timer import TABLE_NAME, CyclicTimer, DateTimer
from madam.domains.entities.workflow import TABLE_NAME as WORKFLOWS_TABLE_NAME
from madam.domains.entities.workflow import Workflow
from madam.domains.interfaces.repository.timers import TimerRepositoryInterface


class PostgreSQLTimerRepository(TimerRepositoryInterface):
    """
    PostgreSQLTimerRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLTimerRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        :return:
        """
        self.client = client

    def create_date_timer(self, timer: DateTimer) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.create_date_timer.__doc__
        )
        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=timer.id,
            start_at=timer.start_at,
            status=timer.status,
            input=timer.input,
            workflow_id=timer.workflow.id,
            workflow_version=timer.workflow.version,
            date=timer.date,
        )

    def create_cyclic_timer(self, timer: CyclicTimer) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.create_cyclic_timer.__doc__
        )
        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=timer.id,
            start_at=timer.start_at,
            status=timer.status,
            input=timer.input,
            workflow_id=timer.workflow.id,
            workflow_version=timer.workflow.version,
            repeat=timer.repeat,
            interval=timer.interval,
        )

    @staticmethod
    def _from_row(row: tuple) -> Union[CyclicTimer, DateTimer]:
        """
        Return CyclicTimer or DateTimer object from result set row

        :param row: Result set row
        :return:
        """
        workflow_nb_columns = 7
        timer_nb_columns = 10
        timer_base_nb_columns = 7
        date_column_index = 7

        workflow = Workflow(*row[-workflow_nb_columns:])
        arguments = list(row[:timer_nb_columns])
        if arguments[date_column_index] is not None:
            date_arguments = (
                arguments[: timer_base_nb_columns - 2]
                + [workflow]
                + [arguments[date_column_index]]
            )
            return DateTimer(*date_arguments)

        cyclic_arguments = (
            arguments[: timer_base_nb_columns - 2]
            + [workflow]
            + arguments[timer_nb_columns - 2 : timer_nb_columns]
        )
        return CyclicTimer(*cyclic_arguments)

    def read(
        self, id: uuid.UUID  # pylint: disable=redefined-builtin
    ) -> Union[CyclicTimer, DateTimer]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.read.__doc__
        )
        timers = Table(TABLE_NAME)
        join = timers.join(Table(WORKFLOWS_TABLE_NAME))
        join.condition = (timers.workflow_id == join.right.id) & (
            timers.workflow_version == join.right.version
        )
        select = join.select()
        select.where = timers.id == id
        sql, args = tuple(select)

        result = self.client.fetch_one(sql, *args)

        return self._from_row(result)

    def update(
        self, id: uuid.UUID, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.update.__doc__
        )
        self.client.update_one(TABLE_NAME, id, **kwargs)

    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.delete.__doc__
        )
        self.client.delete(TABLE_NAME, id=id)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: str = None,
        workflow: Optional[Workflow] = None,
    ) -> List[Union[DateTimer, CyclicTimer]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.list.__doc__
        )
        timers = Table(TABLE_NAME)
        sql_sort_colum = Column(timers, sort_column)
        join = timers.join(Table(WORKFLOWS_TABLE_NAME))
        join.condition = (timers.workflow_id == join.right.id) & (
            timers.workflow_version == join.right.version
        )
        select = join.select(
            order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
            limit=limit,
            offset=offset,
        )

        conditions = []
        if status is not None:
            conditions.append(timers.status == status)
        if workflow is not None:
            conditions.append(
                (timers.workflow_id == workflow.id)
                & (timers.workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)
        result_set = self.client.fetch_all(sql, *args)

        list_: List[Union[DateTimer, CyclicTimer]] = []
        for row in result_set:
            list_.append(self._from_row(row))

        return list_

    def count(self, status: str = None, workflow: Workflow = None) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TimerRepositoryInterface.count.__doc__
        )
        timers = Table(TABLE_NAME)

        select = timers.select(Count(timers.id))
        conditions = []
        if status is not None:
            conditions.append(timers.status == status)
        if workflow is not None:
            conditions.append(
                (timers.workflow_id == workflow.id)
                & (timers.workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]
