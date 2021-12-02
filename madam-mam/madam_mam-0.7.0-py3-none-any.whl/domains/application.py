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
Madam application module
"""
from madam import __version__
from madam.adapters.bpmn.parser import ZeebeeBPMNXMLParser
from madam.adapters.config import YAMLConfigRepository
from madam.adapters.process.applications import DockerApplicationProcessManager
from madam.adapters.repository.applications import PostgreSQLApplicationRepository
from madam.adapters.repository.jobs import PostgreSQLJobRepository
from madam.adapters.repository.postgresql import PostgreSQLClient
from madam.adapters.repository.timers import PostgreSQLTimerRepository
from madam.adapters.repository.watchfolders import PostgreSQLWatchfolderRepository
from madam.adapters.repository.workflow_instances import (
    PostgreSQLWorkflowInstanceRepository,
)
from madam.adapters.repository.workflows import PostgreSQLWorkflowRepository
from madam.domains.agents import Agents
from madam.domains.applications import Applications
from madam.domains.events import EventDispatcher
from madam.domains.jobs import Jobs
from madam.domains.timers import Timers
from madam.domains.watchfolders import Watchfolders
from madam.domains.workflow_instances import WorkflowInstances
from madam.domains.workflows import Workflows
from madam.slots.graphql.api import GraphQLAPI


class MainApplication:
    """
    Madam application class
    """

    def __init__(self, config_path: str):
        """
        Init application with configuration filepath

        :param config_path: Configuration filepath
        """
        ##################################################
        # DEPENDENCY INJECTION
        ##################################################

        # ADAPTERS #######################################
        self.config = YAMLConfigRepository(config_path)
        # Repository
        postgresql_client = PostgreSQLClient(self.config)
        workflow_repository = PostgreSQLWorkflowRepository(postgresql_client)
        workflow_instance_repository = PostgreSQLWorkflowInstanceRepository(
            postgresql_client
        )
        watchfolder_repository = PostgreSQLWatchfolderRepository(postgresql_client)
        timer_repository = PostgreSQLTimerRepository(postgresql_client)
        job_repository = PostgreSQLJobRepository(postgresql_client)
        application_repository = PostgreSQLApplicationRepository(postgresql_client)
        # Process manager
        process_manager = DockerApplicationProcessManager(self.config)
        # BPMN
        bpmn_parser = ZeebeeBPMNXMLParser()

        # DOMAINS #######################################
        self.event_dispatcher = EventDispatcher()
        self.applications = Applications(
            application_repository, process_manager, self.event_dispatcher
        )
        self.jobs = Jobs(job_repository, self.applications, self.event_dispatcher)
        self.workflow_instances = WorkflowInstances(
            workflow_instance_repository,
            self.jobs,
            self.applications,
            self.event_dispatcher,
            bpmn_parser,
        )
        self.timers = Timers(
            timer_repository, self.workflow_instances, self.event_dispatcher
        )
        self.workflows = Workflows(
            workflow_repository,
            self.workflow_instances,
            self.timers,
            self.event_dispatcher,
            bpmn_parser,
        )
        self.watchfolders = Watchfolders(
            watchfolder_repository, self.workflows, self.event_dispatcher
        )
        self.version = __version__
        self.agents = Agents(self.config)

        # SLOTS #######################################
        self.graphql_api = GraphQLAPI(self.event_dispatcher)

    def get_version(self):
        """
        Get application version

        :return:
        """
        return self.version
