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
Madam workflow_instances domain module
"""
import concurrent
import copy
import json
import logging
import uuid
from concurrent.futures import Future, InvalidStateError
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional

from madam.adapters.bpmn.engine import AdhesiveBPMNEngine
from madam.domains.applications import Applications
from madam.domains.entities.application import ApplicationAborted
from madam.domains.entities.events import WorkflowInstanceEvent
from madam.domains.entities.runner import WorkflowInstanceRunner
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import (
    STATUS_ABORTED,
    STATUS_COMPLETE,
    STATUS_ERROR,
    STATUS_RUNNING,
    WorkflowInstance,
)
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.bpmn import BPMNXMLParserInterface
from madam.domains.interfaces.repository.workflow_instances import (
    WorkflowInstanceRepositoryInterface,
)
from madam.domains.jobs import Jobs
from madam.libs.serialize import WorkflowInstanceJSONEncoder


class WorkflowInstances:
    """
    Madam WorkflowInstances domain class
    """

    register: Dict[uuid.UUID, WorkflowInstanceRunner] = {}

    def __init__(
        self,
        repository: WorkflowInstanceRepositoryInterface,
        jobs: Jobs,
        applications: Applications,
        event_dispatcher: EventDispatcher,
        bpmn_parser: BPMNXMLParserInterface,
    ):
        """
        Init WorkflowInstances domain

        :param repository: WorkflowInstanceRepository domain instance
        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        :param event_dispatcher: EventDispatcher instance
        :param bpmn_parser: BPMNXMLParser instance
        """
        self.repository = repository
        self.jobs = jobs
        self.applications = applications
        self.event_dispatcher = event_dispatcher
        self.bpmn_parser = bpmn_parser

    def create(self, workflow: Workflow, variables: dict = None) -> WorkflowInstance:
        """
        Create a WorkflowInstance with an entry in database

        :param workflow: Workflow the instance is created upon
        :param variables: Initial variables (default=None)
        :return:
        """
        workflow_instance = WorkflowInstance(
            id=uuid.uuid4(),
            start_at=datetime.now(),
            end_at=None,
            status=STATUS_RUNNING,
            input=variables,
            output=None,
            error=None,
            workflow=workflow,
        )

        self.repository.create(workflow_instance)

        # dispatch event
        event = WorkflowInstanceEvent(
            WorkflowInstanceEvent.EVENT_TYPE_CREATE,
            copy.copy(workflow_instance),
        )
        self.event_dispatcher.dispatch_event(event)

        return workflow_instance

    def read(self, id_: uuid.UUID) -> WorkflowInstance:
        """
        Get a Workflow instance object by its id_.

        :param id_: Id of the workflow instance
        :return:
        """
        return self.repository.read(id_)

    def update(self, workflow_instance: WorkflowInstance, **kwargs):
        """
        Update kwargs fields of workflow_instance

        :param workflow_instance: WorkflowInstance instance
        :return:
        """
        if "output" in kwargs and kwargs["output"] is not None:
            # variables contains special variable "madam" with serialized workflow_instance
            # remove it before updating workflow_instance
            del kwargs["output"]["madam"]

        # update object
        for key, value in kwargs.items():
            if hasattr(workflow_instance, key):
                setattr(workflow_instance, key, value)

        # update entry in database
        self.repository.update(workflow_instance.id, **kwargs)

        # dispatch event
        event = WorkflowInstanceEvent(
            WorkflowInstanceEvent.EVENT_TYPE_UPDATE,
            copy.copy(workflow_instance),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete(self, workflow_instance: WorkflowInstance):
        """
        Delete workflow instance from database with children and containers

        :param workflow_instance: WorkflowInstance instance
        :return:
        """
        # delete jobs
        self.jobs.delete_by_workflow_instance_id(workflow_instance.id)

        # delete entry in database
        self.repository.delete(workflow_instance.id)

        # dispatch event
        event = WorkflowInstanceEvent(
            WorkflowInstanceEvent.EVENT_TYPE_DELETE,
            copy.copy(workflow_instance),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete_by_workflow(self, workflow: Workflow):
        """
        Delete all workflow instances from parent workflow

        :param workflow: Workflow object
        :return:
        """
        offset = 0
        workflow_instances = self.list(offset=offset, limit=1000, workflow=workflow)
        while len(workflow_instances) > 0:
            for workflow_instance in workflow_instances:
                self.delete(workflow_instance)
            offset += 1000
            workflow_instances = self.list(offset=offset, limit=1000, workflow=workflow)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: Optional[str] = None,
        workflow: Optional[Workflow] = None,
    ) -> List[WorkflowInstance]:
        """
        Return a list of WorkflowInstance objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="start_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param status: Status constant to filter by (default=None)
        :param workflow: Parent workflow to filter by (default=None)
        :return:
        """
        return self.repository.list(
            offset, limit, sort_column, sort_ascending, status, workflow
        )

    @staticmethod
    def _from_row(row: tuple) -> WorkflowInstance:
        """
        Return WorkflowInstance from result set row

        :param row: Result set row
        :return:
        """
        workflow = Workflow(*row[-7:])
        arguments = list(row[:6])
        arguments.append(workflow)
        return WorkflowInstance(*arguments)

    def count(self, status: str = None, workflow: Workflow = None) -> int:
        """
        Return total count of workflow instances

        :param status: Filter by status (default=None)
        :param workflow: Filter by parent Workflow (default=None)
        :return:
        """
        return self.repository.count(status, workflow)

    def start(self, workflow: Workflow, variables: Optional[dict] = None) -> bool:
        """
        Create, start and return workflow instance

        :param workflow: Parent Workflow object
        :param variables: Initial variables (default=None)
        :return:
        """
        workflow_instance = self.create(workflow, variables)
        if workflow_instance is None:
            return False

        self._register_and_start_runner(workflow_instance, variables)

        return True

    def abort(self, workflow_instance: WorkflowInstance):
        """
        Abort workflow_instance future and adhesive process

        :param workflow_instance: WorkflowInstance object
        :return:
        """
        # abort all containers
        self.applications.abort_containers(workflow_instance)
        # if runner for this instance in register...
        if workflow_instance.id in self.register:
            runner = self.register[workflow_instance.id]
            if runner.future is not None:
                # cancel workflow_instance future thread (does not abort adhesive process)
                runner.future.cancel()

                # wait for future to end (make sure adhesive process is terminated)
                concurrent.futures.wait((runner.future,), timeout=None)

        # set STATUS_ABORTED to children jobs and applications
        self.jobs.abort_by_workflow_instance(workflow_instance)

        self.update(workflow_instance, status=STATUS_ABORTED, end_at=datetime.now())

        # if runner for this instance in register...
        if workflow_instance.id in self.register:
            # delete registered runner
            del self.register[workflow_instance.id]

    def synchronous_start(
        self, workflow_instance: WorkflowInstance, variables: Optional[dict] = None
    ):
        """
        Start workflow instance execution

        :param workflow_instance: WorkflowInstance object
        :param variables: Initial variables (default=None)
        :return:
        """
        if variables is None:
            variables = {}
        else:
            variables = dict(variables)

        # agents should have access to parent workflow_instance to create jobs
        variables["madam"] = {
            "workflow_instance": json.dumps(
                workflow_instance, cls=WorkflowInstanceJSONEncoder
            ),
        }

        try:
            # start adhesive process of runner of workflow_instance
            output_data = self.register[workflow_instance.id].bpmn_engine.start(
                variables
            )
        except InvalidStateError:
            # logging.warning(
            #     "workflow instance id=%s adhesive process aborted",
            #     workflow_instance.id_,
            # )
            return
        except ApplicationAborted:
            self.update(
                workflow_instance,
                status=STATUS_ABORTED,
                end_at=datetime.now(),
            )
            return
        except Exception as exception:
            logging.exception(exception)
            self.update(
                workflow_instance,
                status=STATUS_ERROR,
                error=str(exception),
                end_at=datetime.now(),
            )
            return

        self.update(
            workflow_instance,
            output=output_data,
            status=STATUS_COMPLETE,
            end_at=datetime.now(),
        )

    def abort_by_workflow(self, workflow: Workflow):
        """
        Abort all running workflow instances from parent workflow

        :param workflow: Workflow object
        :return:
        """
        offset = 0
        workflow_instances = self.list(
            offset=offset, limit=1000, status=STATUS_RUNNING, workflow=workflow
        )
        while len(workflow_instances) > 0:
            for workflow_instance in workflow_instances:
                self.abort(workflow_instance)
            offset += 1000
            workflow_instances = self.list(
                offset=offset, limit=1000, status=STATUS_RUNNING, workflow=workflow
            )

    def _register_and_start_runner(
        self, workflow_instance: WorkflowInstance, variables: Optional[dict] = None
    ):
        """
        Create workflow_instance, a ProcessExecutor, start a future and register them in a runner

        :param workflow_instance: Parent workflow object
        :param variables: Initial variables (default=None)
        :return:
        """
        # create and register runner
        runner = WorkflowInstanceRunner(
            AdhesiveBPMNEngine(
                workflow_instance.workflow.content,
                self.bpmn_parser,
                self.jobs,
                self.applications,
            ),
            ThreadPoolExecutor(),
            None,
        )
        # store runner in register
        self.register[workflow_instance.id] = runner
        # execute adhesive workflow and store future
        runner.future = runner.instance_executor.submit(
            self.synchronous_start, workflow_instance, variables
        )
        # add callback to delete runner after adhesive workflow ended
        runner.future.add_done_callback(self._remove_runner)

    def _remove_runner(self, future: Future):
        """
        Remove runner after future is done

        :param future: Future completed
        :return:
        """
        index = None
        for workflow_instance_id, runner in self.register.items():
            if runner.future == future:
                index = workflow_instance_id

        if index is not None:
            del self.register[index]
