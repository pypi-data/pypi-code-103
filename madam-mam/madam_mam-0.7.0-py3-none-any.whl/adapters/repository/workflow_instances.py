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
from typing import List, Optional

from sql import Column, Table
from sql.aggregate import Count

from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.domains.entities.workflow import TABLE_NAME as WORKFLOWS_TABLE_NAME
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import TABLE_NAME, WorkflowInstance
from madam.domains.interfaces.repository.workflow_instances import (
    WorkflowInstanceRepositoryInterface,
)


class PostgreSQLWorkflowInstanceRepository(WorkflowInstanceRepositoryInterface):
    """
    PostgreSQLWorkflowInstanceRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLWorkflowInstanceRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        :return:
        """
        self.client = client

    def create(self, workflow_instance: WorkflowInstance):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.create.__doc__
        )
        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=workflow_instance.id,
            start_at=workflow_instance.start_at,
            status=workflow_instance.status,
            input=workflow_instance.input,
            workflow_id=workflow_instance.workflow.id,
            workflow_version=workflow_instance.workflow.version,
        )

    @staticmethod
    def _from_row(row: tuple) -> WorkflowInstance:
        """
        Return WorkflowInstance from result set row

        :param row: Result set row
        :return:
        """
        workflow_instance_nb_columns = 9
        workflow_nb_column = 7

        workflow = Workflow(*row[-workflow_nb_column:])
        arguments = list(row[: workflow_instance_nb_columns - 2])
        arguments.append(workflow)
        return WorkflowInstance(*arguments)

    def read(
        self, id: uuid.UUID  # pylint: disable=redefined-builtin
    ) -> WorkflowInstance:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.read.__doc__
        )
        workflow_instances = Table(TABLE_NAME)
        join = workflow_instances.join(Table(WORKFLOWS_TABLE_NAME))
        join.condition = (workflow_instances.workflow_id == join.right.id) & (
            workflow_instances.workflow_version == join.right.version
        )
        select = join.select()
        select.where = workflow_instances.id == id
        sql, args = tuple(select)

        result = self.client.fetch_one(sql, *args)

        return self._from_row(result)

    def update(self, id: uuid.UUID, **kwargs):  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.update.__doc__
        )
        self.client.update_one(TABLE_NAME, id, **kwargs)

    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.delete.__doc__
        )
        self.client.delete(TABLE_NAME, id=id)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: Optional[str] = None,
        workflow: Optional[Workflow] = None,
    ) -> List[WorkflowInstance]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.list.__doc__
        )
        workflow_instances = Table(TABLE_NAME)
        sql_sort_colum = Column(workflow_instances, sort_column)
        join = workflow_instances.join(Table(WORKFLOWS_TABLE_NAME))
        join.condition = (workflow_instances.workflow_id == join.right.id) & (
            workflow_instances.workflow_version == join.right.version
        )
        select = join.select(
            order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
            limit=limit,
            offset=offset,
        )

        conditions = []
        if status is not None:
            conditions.append(workflow_instances.status == status)
        if workflow is not None:
            conditions.append(
                (workflow_instances.workflow_id == workflow.id)
                & (workflow_instances.workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)
        result_set = self.client.fetch_all(sql, *args)

        list_ = []
        for row in result_set:
            workflow_instance = self._from_row(row)
            list_.append(workflow_instance)

        return list_

    def count(self, status: str = None, workflow: Workflow = None) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowInstanceRepositoryInterface.count.__doc__
        )
        workflow_instances = Table(TABLE_NAME)

        select = workflow_instances.select(Count(workflow_instances.id))
        conditions = []
        if status is not None:
            conditions.append(workflow_instances.status == status)
        if workflow is not None:
            conditions.append(
                (workflow_instances.workflow_id == workflow.id)
                & (workflow_instances.workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]
