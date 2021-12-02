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
Madam applications domain module
"""
import copy
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Union

from madam.domains.entities.application import (
    STATUS_ABORTED,
    STATUS_COMPLETE,
    STATUS_ERROR,
    STATUS_RUNNING,
    Application,
)
from madam.domains.entities.events import ApplicationEvent
from madam.domains.entities.job import Job
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.process.applications import (
    ApplicationProcessManagerInterface,
)
from madam.domains.interfaces.repository.applications import (
    ApplicationRepositoryInterface,
)


class Applications:
    """
    Madam Applications domain class
    """

    def __init__(
        self,
        repository: ApplicationRepositoryInterface,
        process_manager: ApplicationProcessManagerInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Applications domain

        :param repository: ApplicationRepository adapter Instance
        :param process_manager: Config params
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.process_manager = process_manager
        self.event_dispatcher = event_dispatcher

    def create(self, job: Job, name: str, version: str, arguments: str) -> Application:
        """
        Create an Application object with an entry in database

        :param job: Job instance
        :param name: Name of the application
        :param version: Version of the application
        :param arguments: Arguments of the application command
        :return:
        """
        application = Application(
            id=uuid.uuid4(),
            name=name,
            version=version,
            arguments=arguments,
            start_at=datetime.now(),
            end_at=None,
            status=STATUS_RUNNING,
            logs=None,
            container_id=None,
            container_error=None,
            job=job,
        )

        # Create new entry in database
        self.repository.create(application)

        # dispatch event
        event = ApplicationEvent(
            ApplicationEvent.EVENT_TYPE_CREATE,
            copy.copy(application),
        )
        self.event_dispatcher.dispatch_event(event)

        return application

    def read(self, id_: uuid.UUID) -> Application:
        """
        Get an Application object by its ID

        :param id_: ID of the Application
        :return:
        """
        return self.repository.read(id_)

    def update(self, application: Application, **kwargs) -> None:
        """
        Update fields of Application from key=value arguments

        :param application: Application instance
        :return:
        """
        # update object
        for key, value in kwargs.items():
            if hasattr(application, key):
                setattr(application, key, value)

        # Update entry in database
        self.repository.update(application.id, **kwargs)

        # dispatch event
        event = ApplicationEvent(
            ApplicationEvent.EVENT_TYPE_UPDATE,
            copy.copy(application),
        )
        self.event_dispatcher.dispatch_event(event)

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
        return self.repository.list(
            offset, limit, sort_column, sort_ascending, status, job_id
        )

    def count(self, status: str = None, job_id: Optional[uuid.UUID] = None) -> int:
        """
        Return total count of applications

        :param status: Filter by status (default=None)
        :param job_id: Filter by parent Job ID (default=None)
        :return:
        """
        return self.repository.count(status, job_id)

    def run(
        self,
        job: Job,
        name: str,
        version: str,
        arguments: str,
        config: Optional[dict] = None,
        ignore_failure: bool = False,
    ) -> Application:
        """
        Create and run application

        :param job: Parent Job instance
        :param name: Name of the application
        :param version: Version of the application
        :param arguments: Arguments of the application command
        :param config: Configuration for process manager implementation (default=None)
        :param ignore_failure: Set status as complete if docker_api.DOCKER_TASK_STATE_FAILED (default=False)
        :return:
        """
        application = self.create(job, name, version, arguments)

        try:
            self.process_manager.run(application, config)
        except Exception as exception:
            logging.exception(exception)
            self.update(
                application,
                status=STATUS_ERROR,
                container_error=str(exception),
                end_at=datetime.now(),
            )
            return application

        self.update(
            application,
            container_id=application.container_id,
        )

        self.process_manager.wait(application, ignore_failure)

        self.update(
            application,
            status=application.status,
            container_error=application.container_error,
            logs=application.logs,
            end_at=datetime.now(),
        )

        # if it is a container error, keep the container for debug
        if application.status not in (STATUS_COMPLETE, STATUS_ABORTED):
            return application

        # remove process container
        if application.container_id is not None:
            self.process_manager.delete_container(application.container_id)

        return application

    def delete(self, application: Application):
        """
        Delete application from database and his container if any

        :param application: Application instance
        :return:
        """
        if application.container_id is not None:
            self.process_manager.delete_container(application.container_id)

        # delete entry in database
        self.repository.delete(application.id)

        # dispatch event
        event = ApplicationEvent(
            ApplicationEvent.EVENT_TYPE_DELETE,
            copy.copy(application),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete_by_job_id(self, job_id: uuid.UUID):
        """
        Delete applications with parent job_id

        :param job_id: Id of the parent Job
        :return:
        """
        applications = self.list(job_id=job_id)
        for application in applications:
            self.delete(application)

    def abort_containers(
        self, parent: Union[Workflow, WorkflowInstance, Job, Application]
    ):
        """
        Abort all containers created from parent

        :param parent: Workflow, WorkflowInstance, Job or Application object
        :return:
        """
        container_ids = self.repository.get_container_ids_by_parent(parent)
        for container_id in container_ids:
            if container_id is None:
                continue
            self.process_manager.abort_container(container_id)

    def abort_by_job_ids(self, ids: List[uuid.UUID]):
        """
        Set STATUS_ABORTED to applications with job ids as parents in repository

        :param ids: List of job ids
        :return:
        """
        self.repository.update_by_job_ids(
            ids, status=STATUS_ABORTED, end_at=datetime.now()
        )
