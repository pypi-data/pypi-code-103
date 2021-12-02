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

from typing import List, Optional

from sql import Column, Literal, Table
from sql.aggregate import Count, Max

from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.domains.entities.workflow import TABLE_NAME, Workflow
from madam.domains.interfaces.repository.workflows import WorkflowRepositoryInterface


class PostgreSQLWorkflowRepository(WorkflowRepositoryInterface):
    """
    PostgreSQLWorkflowRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLWorkflowRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        """
        self.client = client

    def create(self, workflow: Workflow) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.create.__doc__
        )

        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=workflow.id,
            version=workflow.version,
            name=workflow.name,
            content=workflow.content,
            sha256=workflow.sha256,
            timer=workflow.timer,
            created_at=workflow.created_at,
        )

    def read(
        self,
        id: str,  # pylint: disable=redefined-builtin
        version: Optional[int] = None,
    ) -> Workflow:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.read.__doc__
        )

        workflows = Table(TABLE_NAME)
        select = workflows.select()

        if version is not None:
            # get workflow by version
            select.where = (workflows.id == Literal(id)) & (
                workflows.version == version
            )
        else:
            # get last version
            select.where = workflows.id == Literal(id)
            select.order_by = workflows.version.desc

        sql, args = tuple(select)
        result = self.client.fetch_one(sql, *args)

        if result:
            return Workflow(*result)

        raise Exception("Workflow not found")

    def delete(self, id: str):  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.delete.__doc__
        )

        # delete entry in database
        self.client.delete(TABLE_NAME, id=id)

    def get_last_version_by_id(
        self, id: str  # pylint: disable=redefined-builtin
    ) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.get_last_version_by_id.__doc__
        )

        # noinspection SqlResolve
        sql = f"SELECT MAX(version) FROM {TABLE_NAME} WHERE id=%s"

        result = self.client.fetch_one(sql, id)
        if result[0]:
            return result[0]

        return 0

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "created_at",
        sort_ascending: bool = True,
        last_version: bool = False,
    ) -> List[Workflow]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.list.__doc__
        )

        workflows = Table(TABLE_NAME)
        sql_sort_colum = Column(workflows, sort_column)
        if last_version is True:
            # select workflows.id, grouped.mv as version
            # from workflows, (select id, max(version) as mv from workflows group by id) as grouped
            # where workflows.id = grouped.id and workflows.version = grouped.mv
            grouped_select = workflows.select(
                workflows.id, Max(workflows.version).as_("mv"), group_by=workflows.id
            )
            tables = workflows + grouped_select
            select = tables.select(
                workflows.id,
                grouped_select.mv,
                workflows.name,
                workflows.content,
                workflows.sha256,
                workflows.timer,
                workflows.created_at,
                order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
                limit=limit,
                offset=offset,
                where=(
                    (workflows.id == grouped_select.id)
                    & (workflows.version == grouped_select.mv)
                ),
            )
        else:
            select = workflows.select(
                order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
                limit=limit,
                offset=offset,
            )

        sql, args = tuple(select)

        return [Workflow(*row) for row in self.client.fetch_all(sql, *args)]

    def count(self, last_version: bool = False) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WorkflowRepositoryInterface.count.__doc__
        )

        workflows = Table(TABLE_NAME)
        if last_version is True:
            # select workflows.id, grouped.mv as version
            # from workflows, (select id, max(version) as mv from workflows group by id) as grouped
            # where workflows.id = grouped.id and workflows.version = grouped.mv
            grouped_select = workflows.select(
                workflows.id, Max(workflows.version).as_("mv"), group_by=workflows.id
            )
            select = grouped_select.select(Count(grouped_select.id))
        else:
            select = workflows.select(Count(workflows.id))

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]
