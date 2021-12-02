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

"""
Madam jobs domain module
"""
import copy
import uuid
from datetime import datetime
from typing import List, Optional

from madam.domains.applications import Applications
from madam.domains.entities.events import JobEvent
from madam.domains.entities.job import STATUS_ABORTED, STATUS_RUNNING, Job
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.repository.jobs import JobRepositoryInterface


class Jobs:
    """
    Madam Jobs domain class
    """

    def __init__(
        self,
        repository: JobRepositoryInterface,
        applications: Applications,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Jobs domain

        :param repository: JobRepository adapter Instance
        :param applications: Applications domain instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.applications = applications
        self.event_dispatcher = event_dispatcher

    def create(
        self,
        workflow_instance: WorkflowInstance,
        agent_id: str,
        agent_type: str,
        headers: dict,
        input_: dict,
    ) -> Job:
        """
        Create a Job object with an entry in database

        :param workflow_instance: WorkflowInstance object
        :param agent_id: Id of the agent
        :param agent_type: Type of the agent
        :param headers: Headers parameters
        :param input_: Local input variables
        :return:
        """
        # input_ contains special variable "madam" with serialized workflow_instance
        # remove it before creating job
        if "madam" in input_:
            del input_["madam"]

        job = Job(
            uuid.uuid4(),
            agent_id,
            agent_type,
            datetime.now(),
            None,
            STATUS_RUNNING,
            headers,
            input_,
            None,
            None,
            workflow_instance,
        )

        # Create new entry in database
        self.repository.create(job)

        # dispatch event
        event = JobEvent(
            JobEvent.EVENT_TYPE_CREATE,
            copy.copy(job),
        )
        self.event_dispatcher.dispatch_event(event)

        return job

    def read(self, id_: uuid.UUID) -> Job:
        """
        Get a Job object by its id_.

        :param id_: Id of the Job
        :return:
        """
        return self.repository.read(id_)

    def update(self, job: Job, **kwargs) -> None:
        """
        Update fields of job from key=value arguments

        :param job: Job instance
        :return:
        """
        # update object
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # Update entry in database
        self.repository.update(job.id, **kwargs)

        # dispatch event
        event = JobEvent(
            JobEvent.EVENT_TYPE_UPDATE,
            copy.copy(job),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete(self, job: Job) -> None:
        """
        Delete Job instance from database with children and containers

        :param job: Job instance
        :return:
        """
        # delete applications
        self.applications.delete_by_job_id(job.id)

        # delete entry in database
        self.repository.delete(job.id)

        # dispatch event
        event = JobEvent(
            JobEvent.EVENT_TYPE_DELETE,
            copy.copy(job),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete_by_workflow_instance_id(self, workflow_instance_id: uuid.UUID):
        """
        Delete jobs with parent workflow_instance_id

        :param workflow_instance_id: Parent WorkflowInstance id
        :return:
        """
        offset = 0
        jobs = self.list(
            offset=offset, limit=1000, workflow_instance_id=workflow_instance_id
        )
        while len(jobs) > 0:
            for job in jobs:
                self.delete(job)
            offset += 1000
            jobs = self.list(
                offset=offset, limit=1000, workflow_instance_id=workflow_instance_id
            )

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
        return self.repository.list(
            offset, limit, sort_column, sort_ascending, status, workflow_instance_id
        )

    def count(self, status: str = None, instance_id: Optional[uuid.UUID] = None) -> int:
        """
        Return total count of jobs

        :param status: Filter by status (default=None)
        :param instance_id: Filter by parent WorkflowInstance ID (default=None)
        :return:
        """
        return self.repository.count(status, instance_id)

    def abort_by_workflow_instance(self, workflow_instance: WorkflowInstance):
        """
        Set STATUS_ABORTED to jobs with workflow_instance as parent
        Abort children applications of jobs

        :param workflow_instance: WorkflowInstance object
        :return:
        """
        self.repository.update_by_workflow_instance_id(
            workflow_instance.id, status=STATUS_ABORTED, end_at=datetime.now()
        )

        ids = self.repository.get_ids_by_workflow_instance_id(workflow_instance.id)

        if len(ids) > 1:
            self.applications.abort_by_job_ids(ids)
