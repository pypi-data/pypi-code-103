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
import json
import uuid
from functools import reduce
from typing import List, Optional

from sql import Column, Table
from sql.aggregate import Count

from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.domains.entities.job import TABLE_NAME, Job
from madam.domains.entities.workflow import TABLE_NAME as WORKFLOWS_TABLE_NAME
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import (
    TABLE_NAME as WORKFLOW_INSTANCES_TABLE_NAME,
)
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.interfaces.repository.jobs import JobRepositoryInterface


class PostgreSQLJobRepository(JobRepositoryInterface):
    """
    PostgreSQLJobRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLJobRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        :return:
        """
        self.client = client

    def create(self, job: Job) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.create.__doc__
        )
        # Create new entry in database
        self.client.insert(
            TABLE_NAME,
            id=job.id,
            agent_id=job.agent_id,
            agent_type=job.agent_type,
            start_at=job.start_at,
            status=job.status,
            headers=json.dumps(job.headers),
            input=json.dumps(job.input),
            workflow_instance_id=job.workflow_instance.id,
        )

    @staticmethod
    def _from_row(row: tuple) -> Job:
        """
        Return Job object from result set row

        :param row: Result set row
        :return:
        """
        job_nb_columns = 11
        workflow_instance_nb_columns = 9

        workflow = Workflow(*row[job_nb_columns + workflow_instance_nb_columns :])
        workflow_instance_arguments = list(
            row[job_nb_columns : job_nb_columns + workflow_instance_nb_columns - 2]
        )
        workflow_instance_arguments.append(workflow)
        workflow_instance = WorkflowInstance(*workflow_instance_arguments)
        job_arguments = list(row[0 : job_nb_columns - 1])
        job_arguments.append(workflow_instance)
        return Job(*job_arguments)

    def read(self, id: uuid.UUID) -> Job:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.read.__doc__
        )
        jobs = Table(TABLE_NAME)
        join_workflow_instances = jobs.join(Table(WORKFLOW_INSTANCES_TABLE_NAME))
        join_workflow_instances.condition = (
            jobs.workflow_instance_id == join_workflow_instances.right.id
        )

        join_workflows = join_workflow_instances.join(Table(WORKFLOWS_TABLE_NAME))
        join_workflows.condition = (
            join_workflow_instances.right.workflow_id == join_workflows.right.id
        ) & (
            join_workflow_instances.right.workflow_version
            == join_workflows.right.version
        )

        select = join_workflows.select()
        select.where = jobs.id == id
        sql, args = tuple(select)

        result = self.client.fetch_one(sql, *args)

        return self._from_row(result)

    def update(self, id: uuid.UUID, **kwargs):  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.update.__doc__
        )
        self.client.update_one(TABLE_NAME, id, **kwargs)

    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.delete.__doc__
        )
        self.client.delete(TABLE_NAME, id=id)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: Optional[str] = None,
        workflow_instance_id: Optional[uuid.UUID] = None,
    ) -> List[Job]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.list.__doc__
        )
        # SELECT * FROM jobs JOIN workflow_instances wi on jobs.workflow_instance_id = wi.id
        # JOIN workflows w on w.id = wi.workflow_id and w.version = wi.workflow_version
        # ORDER BY jobs.start_at ASC OFFSET 0 LIMIT 1000;

        jobs = Table(TABLE_NAME)
        sql_sort_colum = Column(jobs, sort_column)

        join_workflow_instances = jobs.join(Table(WORKFLOW_INSTANCES_TABLE_NAME))
        join_workflow_instances.condition = (
            jobs.workflow_instance_id == join_workflow_instances.right.id
        )

        join_workflows = join_workflow_instances.join(Table(WORKFLOWS_TABLE_NAME))
        join_workflows.condition = (
            join_workflow_instances.right.workflow_id == join_workflows.right.id
        ) & (
            join_workflow_instances.right.workflow_version
            == join_workflows.right.version
        )

        select = join_workflows.select(
            order_by=sql_sort_colum.asc if sort_ascending else sql_sort_colum.desc,
            limit=limit,
            offset=offset,
        )

        conditions = []
        if status is not None:
            conditions.append(jobs.status == status)
        if workflow_instance_id is not None:
            conditions.append(jobs.workflow_instance_id == workflow_instance_id)

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)
        result_set = self.client.fetch_all(sql, *args)

        list_ = []
        for row in result_set:
            list_.append(self._from_row(row))

        return list_

    def count(self, status: str = None, instance_id: Optional[uuid.UUID] = None) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.count.__doc__
        )
        jobs = Table(TABLE_NAME)

        select = jobs.select(Count(jobs.id))
        conditions = []
        if status is not None:
            conditions.append(jobs.status == status)
        if instance_id is not None:
            conditions.append(jobs.workflow_instance_id == instance_id)

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]

    def update_by_workflow_instance_id(
        self, id, **kwargs  # pylint: disable=redefined-builtin
    ):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.update_by_workflow_instance_id.__doc__
        )
        where = f"workflow_instance_id='{id}'"
        self.client.update(TABLE_NAME, where, **kwargs)

    def get_ids_by_workflow_instance_id(
        self, id  # pylint: disable=redefined-builtin
    ) -> List[uuid.UUID]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            JobRepositoryInterface.count.__doc__
        )
        result_set = self.client.fetch_all(
            "SELECT id FROM jobs WHERE workflow_instance_id=%s", id
        )
        return [row[0] for row in result_set]
