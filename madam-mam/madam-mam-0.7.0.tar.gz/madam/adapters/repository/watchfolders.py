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
from sql.operators import In

from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.domains.entities.watchfolder import TABLE_NAME, Watchfolder
from madam.domains.entities.workflow import TABLE_NAME as WORKFLOWS_TABLE_NAME
from madam.domains.entities.workflow import Workflow
from madam.domains.interfaces.repository.watchfolders import (
    WatchfolderRepositoryInterface,
)


class PostgreSQLWatchfolderRepository(WatchfolderRepositoryInterface):
    """
    PostgreSQLWatchfolderRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLWatchfolderRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        :return:
        """
        self.client = client

    def create(self, watchfolder: Watchfolder) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.create.__doc__
        )
        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=watchfolder.id,
            path=watchfolder.path,
            start_at=watchfolder.start_at,
            status=watchfolder.status,
            re_files=watchfolder.re_files,
            re_dirs=watchfolder.re_dirs,
            added_workflow_id=None
            if watchfolder.added_workflow is None
            else watchfolder.added_workflow.id,
            added_workflow_version=None
            if watchfolder.added_workflow is None
            else watchfolder.added_workflow.version,
            added_variables=None
            if watchfolder.added_workflow is None
            else watchfolder.added_variables,
            modified_workflow_id=None
            if watchfolder.modified_workflow is None
            else watchfolder.modified_workflow.id,
            modified_workflow_version=None
            if watchfolder.modified_workflow is None
            else watchfolder.modified_workflow.version,
            modified_variables=None
            if watchfolder.modified_workflow is None
            else watchfolder.modified_variables,
            deleted_workflow_id=None
            if watchfolder.deleted_workflow is None
            else watchfolder.deleted_workflow.id,
            deleted_workflow_version=None
            if watchfolder.deleted_workflow is None
            else watchfolder.deleted_workflow.version,
            deleted_variables=None
            if watchfolder.deleted_workflow is None
            else watchfolder.deleted_variables,
            added_items_key=watchfolder.added_items_key,
            modified_items_key=watchfolder.modified_items_key,
            deleted_items_key=watchfolder.deleted_items_key,
        )

    def _from_row(self, row: tuple) -> Watchfolder:
        """
        Return Watchfolder object from result set row

        :param row: Result set row
        :return:
        """
        nb_columns = 19

        arguments = list(row[:7])
        workflow_ids = []
        added_workflow_key = (
            None
            if row[nb_columns - 12] is None
            else tuple(row[nb_columns - 12 : nb_columns - 10])
        )
        added_workflow_variables = row[nb_columns - 10]
        modified_workflow_key = (
            None
            if row[nb_columns - 9] is None
            else tuple(row[nb_columns - 9 : nb_columns - 7])
        )
        modified_workflow_variables = row[nb_columns - 7]
        deleted_workflow_key = (
            None
            if row[nb_columns - 6] is None
            else tuple(row[nb_columns - 6 : nb_columns - 4])
        )
        deleted_workflow_variables = row[nb_columns - 4]

        if row[nb_columns - 12] is not None:
            workflow_ids.append(added_workflow_key)
        if row[nb_columns - 9] is not None:
            workflow_ids.append(modified_workflow_key)
        if row[nb_columns - 6] is not None:
            workflow_ids.append(deleted_workflow_key)

        # get workflows from ids
        workflows = Table(WORKFLOWS_TABLE_NAME)
        select = workflows.select()
        if workflow_ids:
            select.where = In((workflows.id, workflows.version), workflow_ids)
        sql, args = tuple(select)
        result = self.client.fetch_all(sql, *args)
        workflows = {}
        for row_ in result:
            workflows[tuple(row_[0:2])] = Workflow(*row_)

        arguments.append(
            None if added_workflow_key is None else workflows[added_workflow_key]
        )
        arguments.append(added_workflow_variables)
        arguments.append(
            None if modified_workflow_key is None else workflows[modified_workflow_key]
        )
        arguments.append(modified_workflow_variables)
        arguments.append(
            None if deleted_workflow_key is None else workflows[deleted_workflow_key]
        )
        arguments.append(deleted_workflow_variables)
        arguments += row[-3:]

        return Watchfolder(*arguments)

    def read(self, id: uuid.UUID) -> Watchfolder:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.read.__doc__
        )
        watchfolders = Table(TABLE_NAME)
        select = watchfolders.select()
        select.where = watchfolders.id == id
        sql, args = tuple(select)
        result = self.client.fetch_one(sql, *args)

        if result:
            return self._from_row(result)

        raise Exception("Watchfolder not found")

    def update(self, id: uuid.UUID, **kwargs):  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.update.__doc__
        )
        # attributes to column mapping
        columns = dict(kwargs)

        if "added_workflow" in columns:
            del columns["added_workflow"]
            columns["added_workflow_id"] = (
                None
                if kwargs["added_workflow"] is None
                else kwargs["added_workflow"].id
            )
            columns["added_workflow_version"] = (
                None
                if kwargs["added_workflow"] is None
                else kwargs["added_workflow"].version
            )
        if "modified_workflow" in columns:
            del columns["modified_workflow"]
            columns["modified_workflow_id"] = (
                None
                if kwargs["modified_workflow"] is None
                else kwargs["modified_workflow"].id
            )
            columns["modified_workflow_version"] = (
                None
                if kwargs["modified_workflow"] is None
                else kwargs["modified_workflow"].version
            )
        if "deleted_workflow" in columns:
            del columns["deleted_workflow"]
            columns["deleted_workflow_id"] = (
                None
                if kwargs["deleted_workflow"] is None
                else kwargs["deleted_workflow"].id
            )
            columns["deleted_workflow_version"] = (
                None
                if kwargs["deleted_workflow"] is None
                else kwargs["deleted_workflow"].version
            )

        # update entry in database
        self.client.update_one(TABLE_NAME, id, **columns)

    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.delete.__doc__
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
    ) -> List[Watchfolder]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.list.__doc__
        )
        watchfolders = Table(TABLE_NAME)
        sql_sort_colum = Column(watchfolders, sort_column)
        select = watchfolders.select(
            order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
            limit=limit,
            offset=offset,
        )

        conditions = []
        if status is not None:
            conditions.append(watchfolders.status == status)
        if workflow is not None:
            conditions.append(
                (watchfolders.added_workflow_id == workflow.id)
                & (watchfolders.added_workflow_version == workflow.version)
                | (watchfolders.modified_workflow_id == workflow.id)
                & (watchfolders.modified_workflow_version == workflow.version)
                | (watchfolders.deleted_workflow_id == workflow.id)
                & (watchfolders.deleted_workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)
        result_set = self.client.fetch_all(sql, *args)

        list_: List[Watchfolder] = []
        for row in result_set:
            list_.append(self._from_row(row))

        return list_

    def count(self, status: str = None, workflow: Workflow = None) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            WatchfolderRepositoryInterface.count.__doc__
        )
        watchfolders = Table(TABLE_NAME)

        select = watchfolders.select(Count(watchfolders.id))
        conditions = []
        if status is not None:
            conditions.append(watchfolders.status == status)
        if workflow is not None:
            conditions.append(
                (watchfolders.added_workflow_id == workflow.id)
                & (watchfolders.added_workflow_version == workflow.version)
                | (watchfolders.modified_workflow_id == workflow.id)
                & (watchfolders.modified_workflow_version == workflow.version)
                | (watchfolders.deleted_workflow_id == workflow.id)
                & (watchfolders.deleted_workflow_version == workflow.version)
            )

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]
