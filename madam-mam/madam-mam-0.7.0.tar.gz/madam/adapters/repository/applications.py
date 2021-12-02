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
from madam.domains.entities.application import TABLE_NAME, Application
from madam.domains.entities.job import TABLE_NAME as JOBS_TABLE_NAME
from madam.domains.entities.job import Job
from madam.domains.entities.workflow import TABLE_NAME as WORKFLOWS_TABLE_NAME
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import (
    TABLE_NAME as WORKFLOW_INSTANCES_TABLE_NAME,
)
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.interfaces.repository.applications import (
    ApplicationRepositoryInterface,
)


class PostgreSQLApplicationRepository(ApplicationRepositoryInterface):
    """
    PostgreSQLApplicationRepository class
    """

    def __init__(self, client: PostgreSQLClient) -> None:
        """
        Init PostgreSQLApplicationRepository instance with PostgreSQL client

        :param client: PostgreSQLClient instance
        :return:
        """
        self.client = client

    def create(self, application: Application) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.create.__doc__
        )
        self.client.insert(
            TABLE_NAME,
            id=application.id,
            name=application.name,
            version=application.version,
            arguments=application.arguments,
            start_at=application.start_at,
            status=application.status,
            job_id=application.job.id,
        )

    @staticmethod
    def _from_row(row: tuple) -> Application:
        """
        Return Application object from result set row

        :param row: Result set row
        :return:
        """
        application_nb_columns = 11
        job_nb_columns = 11
        workflow_instance_nb_columns = 9

        workflow = Workflow(
            *row[
                application_nb_columns + job_nb_columns + workflow_instance_nb_columns :
            ]
        )
        workflow_instance_arguments = list(
            row[
                application_nb_columns
                + job_nb_columns : application_nb_columns
                + job_nb_columns
                + workflow_instance_nb_columns
                - 2
            ]
        )
        workflow_instance_arguments.append(workflow)
        workflow_instance = WorkflowInstance(*workflow_instance_arguments)
        job_arguments = list(
            row[application_nb_columns : application_nb_columns + job_nb_columns - 1]
        )
        job_arguments.append(workflow_instance)
        job = Job(*job_arguments)
        application_arguments = list(row[0 : application_nb_columns - 1])
        application_arguments.append(job)
        return Application(*application_arguments)

    def read(self, id: uuid.UUID) -> Application:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.read.__doc__
        )
        applications = Table(TABLE_NAME)

        join_jobs = applications.join(Table(JOBS_TABLE_NAME))
        join_jobs.condition = applications.job_id == join_jobs.right.id

        join_workflow_instances = join_jobs.join(Table(WORKFLOW_INSTANCES_TABLE_NAME))
        join_workflow_instances.condition = (
            join_jobs.right.workflow_instance_id == join_workflow_instances.right.id
        )

        join_workflows = join_workflow_instances.join(Table(WORKFLOWS_TABLE_NAME))
        join_workflows.condition = (
            join_workflow_instances.right.workflow_id == join_workflows.right.id
        ) & (
            join_workflow_instances.right.workflow_version
            == join_workflows.right.version
        )

        select = join_workflows.select()
        select.where = applications.id == id
        sql, args = tuple(select)

        result = self.client.fetch_one(sql, *args)

        return self._from_row(result)

    def update(
        self, id: uuid.UUID, **kwargs  # pylint: disable=redefined-builtin
    ) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.update.__doc__
        )
        self.client.update_one(TABLE_NAME, id, **kwargs)

    def delete(self, id: uuid.UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.delete.__doc__
        )
        self.client.delete(TABLE_NAME, id=id)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: str = None,
        job_id: Optional[uuid.UUID] = None,
    ) -> List[Application]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.list.__doc__
        )
        # sql = (
        #     f"SELECT * FROM {TABLE_NAME} AS applications"
        #     f" JOIN {JOBS_TABLE_NAME} on applications.job_id = jobs.id"
        #     f" JOIN {WORKFLOW_INSTANCES_TABLE_NAME} wi on jobs.workflow_instance_id = wi.id"
        #     f" JOIN {WORKFLOWS_TABLE_NAME} w on w.id = wi.workflow_id and w.version = wi.workflow_version"
        # )

        applications = Table(TABLE_NAME)
        sql_sort_colum = Column(applications, sort_column)

        join_jobs = applications.join(Table(JOBS_TABLE_NAME))
        join_jobs.condition = applications.job_id == join_jobs.right.id

        join_workflow_instances = join_jobs.join(Table(WORKFLOW_INSTANCES_TABLE_NAME))
        join_workflow_instances.condition = (
            join_jobs.right.workflow_instance_id == join_workflow_instances.right.id
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
            conditions.append(applications.status == status)
        if job_id is not None:
            conditions.append(applications.job_id == job_id)

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

    def count(self, status: str = None, job_id: Optional[uuid.UUID] = None) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.count.__doc__
        )
        applications = Table(TABLE_NAME)

        select = applications.select(Count(applications.id))
        conditions = []
        if status is not None:
            conditions.append(applications.status == status)
        if job_id is not None:
            conditions.append(applications.job_id == job_id)

        def and_(a, b):
            return a & b

        if len(conditions) > 0:
            select.where = reduce(and_, conditions)

        sql, args = tuple(select)

        return self.client.fetch_one(sql, *args)[0]

    def get_container_ids_by_parent(
        self, parent: Union[Workflow, WorkflowInstance, Job, Application]
    ) -> List[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.get_container_ids_by_parent.__doc__
        )
        # SELECT container_id FROM applications JOIN jobs on applications.job_id = jobs.id JOIN workflow_instances on
        # jobs.workflow_instance_id = workflow_instances.id JOIN workflows on workflows.id =
        # workflow_instances.workflow_id and workflows.version = workflow_instances.workflow_version WHERE
        # workflows.id = '1' OFFSET 0 LIMIT 1000;
        sql = f"SELECT container_id FROM {TABLE_NAME} AS applications"

        if isinstance(parent, (Workflow, WorkflowInstance, Job)):
            sql += f" JOIN {JOBS_TABLE_NAME} jobs on applications.job_id = jobs.id"
            if isinstance(parent, (Workflow, WorkflowInstance)):
                sql += (
                    f" JOIN {WORKFLOW_INSTANCES_TABLE_NAME} workflow_instances on jobs.workflow_instance_id = "
                    "workflow_instances.id "
                )
                if isinstance(parent, Workflow):
                    sql += (
                        f" JOIN {WORKFLOWS_TABLE_NAME} workflows on workflows.id = workflow_instances.workflow_id "
                        "and workflows.version = workflow_instances.workflow_version"
                        " WHERE workflows.id = %s"
                    )
                    result_set = self.client.fetch_all(sql, parent.id)
                else:
                    # parent is a WorkflowInstance
                    sql += " WHERE workflow_instances.id = %s"
                    result_set = self.client.fetch_all(sql, parent.id)
            else:
                # parent is a Job
                sql += " WHERE jobs.id = %s"
                result_set = self.client.fetch_all(sql, parent.id)
        else:
            # parent is an Application
            sql += " WHERE applications.id = %s"
            result_set = self.client.fetch_all(sql, parent.id)

        return [row[0] for row in result_set]

    def update_by_job_ids(self, ids: List[uuid.UUID], **kwargs) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationRepositoryInterface.update_by_job_ids.__doc__
        )
        in_ = ",".join([f"'{id_}'" for id_ in ids])
        where = f"job_id IN ({in_})"
        self.client.update(TABLE_NAME, where, **kwargs)
