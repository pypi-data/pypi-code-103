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
Madam workflows domain module
"""
import copy
import logging
from datetime import datetime
from hashlib import sha256
from typing import List, Optional

import adhesive

from madam.domains.entities.events import WorkflowEvent
from madam.domains.entities.workflow import Workflow
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.bpmn import BPMNXMLParserInterface
from madam.domains.interfaces.repository.workflows import WorkflowRepositoryInterface
from madam.domains.timers import Timers
from madam.domains.workflow_instances import WorkflowInstances


class WorkflowXMLException(Exception):
    """
    WorkflowXMLException class
    """


class WorkflowException(Exception):
    """
    WorkflowException class
    """


class Workflows:
    """
    Madam Workflows domain class
    """

    def __init__(
        self,
        repository: WorkflowRepositoryInterface,
        workflow_instances: WorkflowInstances,
        timers: Timers,
        event_dispatcher: EventDispatcher,
        bpmn_parser: BPMNXMLParserInterface,
    ):
        """
        Init Workflows domain

        :param repository: WorkflowRepository domain instance
        :param workflow_instances: WorkflowIntances domain instance
        :param timers: Timers domain instance
        :param event_dispatcher: EventDispatcher instance
        :param bpmn_parser: BPMNXMLParser instance
        """
        self.repository = repository
        self.workflow_instances = workflow_instances
        self.timers = timers
        self.event_dispatcher = event_dispatcher
        self.bpmn_parser = bpmn_parser

    def create(self, content: str) -> Workflow:
        """
        Create and return a workflow, if not already exists...

        :param content: XML content
        :return:
        """
        content = content.strip()

        # validate BPMN xml
        self.bpmn_parser.validate_xml_schema(content)

        # adhesive check on XML
        adhesive.get_process_executor_from_content(content)

        # get BPMN workflow data
        data = self.bpmn_parser.get_workflow_data(content)

        # get the checksum of the content
        sha256sum = sha256(content.encode("utf-8")).hexdigest()

        try:
            last_workflow = self.read(data.id)  # type: Optional[Workflow]
        except Exception:
            last_workflow = None

        # if workflow is already the last version, cancel
        if last_workflow is not None and sha256sum == last_workflow.sha256:
            logging.warning(
                "This workflow content is already the last version for id %s !", data.id
            )
            return last_workflow
        # Get last version from repository in workflow id_ list, 0 if list empty
        version = self.repository.get_last_version_by_id(data.id)
        # create workflow with version + 1
        workflow = Workflow(
            data.id,
            version + 1,
            data.name,
            content,
            sha256sum,
            data.timer,
            datetime.now(),
        )

        self.repository.create(workflow)

        # dispatch event
        event = WorkflowEvent(
            WorkflowEvent.EVENT_TYPE_CREATE,
            copy.copy(workflow),
        )
        self.event_dispatcher.dispatch_event(event)

        return workflow

    def read(self, id_: str, version: Optional[int] = None) -> Workflow:
        """
        Get a Workflow object by its id_ and version.
        If version is None, the last version is returned.

        :param id_: Id of the workflow
        :param version: Version number
        :return:
        """
        return self.repository.read(id_, version)

    def delete(self, workflow: Workflow):
        """
        Delete workflow from database with children and containers

        :param workflow: Workflow object
        :return:
        """
        # delete workflow instances
        self.workflow_instances.delete_by_workflow(workflow)
        # delete entry in database
        self.repository.delete(workflow.id)

        # dispatch event
        event = WorkflowEvent(
            WorkflowEvent.EVENT_TYPE_DELETE,
            copy.copy(workflow),
        )
        self.event_dispatcher.dispatch_event(event)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "created_at",
        sort_ascending: bool = True,
        last_version: bool = False,
    ) -> List[Workflow]:
        """
        Return a list of Workflow objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="created_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param last_version: Only last version for each workflow (default=False)
        :return:
        """
        return self.repository.list(
            offset, limit, sort_column, sort_ascending, last_version
        )

    def count(self, last_version: bool = False) -> int:
        """
        Return total count of workflows

        :param last_version: Filter to get only last_version if True (default=False)
        :return:
        """
        return self.repository.count(last_version)

    def start(
        self, id_: str, version: Optional[int] = None, variables: Optional[dict] = None
    ) -> bool:
        """
        Start a workflow instance of workflow id_

        :param id_: Id of the workflow
        :param version: Version, if None, use last version (default=None)
        :param variables: Initial variables (default=None)
        :return:
        """
        workflow = self.read(id_, version)
        if workflow is None:
            return False

        if workflow.timer is not None:
            # create and start a timer in background
            return self.timers.start(workflow, variables)

        # create and start workflow instance in background
        return self.workflow_instances.start(workflow, variables)

    def abort(self, id_: str, version: Optional[int] = None) -> bool:
        """
        Abort all workflow instances and the timer (if any) of workflow id_

        :param id_: Id of the workflow
        :param version: Version, if None, use last version (default=None)
        :return:
        """
        workflow = self.read(id_, version)
        if workflow is None:
            return False

        if workflow.timer is not None:
            # abort the timer
            self.timers.abort_by_workflow(workflow)

        self.workflow_instances.abort_by_workflow(workflow)
        return True
