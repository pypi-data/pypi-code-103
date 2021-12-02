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
Madam python agent module
"""
import json
from datetime import datetime

import adhesive
import jinja2

from madam.adapters.interfaces.agents import AdhesiveApplicationAgentInterface
from madam.domains.applications import Applications
from madam.domains.entities.application import (
    STATUS_ABORTED as APPLICATION_STATUS_ABORTED,
)
from madam.domains.entities.application import (
    STATUS_COMPLETE as APPLICATION_STATUS_COMPLETE,
)
from madam.domains.entities.application import (
    AgentApplication,
    ApplicationAborted,
    ApplicationError,
)
from madam.domains.entities.job import STATUS_COMPLETE, STATUS_ERROR, Job
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.jobs import Jobs
from madam.libs.serialize import WorkflowInstanceJSONDecoder


class AdhesivePythonAgent(AdhesiveApplicationAgentInterface):
    """
    AdhesivePythonAgent class
    """

    AGENT_TYPE = "python"
    APPLICATIONS = {"python": AgentApplication("python", "latest")}

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs, applications: Applications) -> None:
        """
        Init AdhesivePythonAgent with domains

        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        self.jobs = jobs
        self.applications = applications

    def execute(self, context: adhesive.ExecutionToken) -> None:
        """
        Execute application python with arguments provided

        Headers:
            arguments:  string with bash arguments parsed as a jinja2 string
                        (workflow variables can be used with jinja2 tags, see https://jinja.palletsprojects.com/en/3.0.x/templates/#variables)

            applications.python.version: Optional[string] with version for python label application

        Example: arguments = "/path/to/python_script.py {{source}} {{destination}}"

        :param context: Adhesive context instance
        :return:
        """
        # job tracking
        workflow_instance = json.loads(
            context.data.madam["workflow_instance"], cls=WorkflowInstanceJSONDecoder
        )  # type: WorkflowInstance
        job = self.jobs.create(
            workflow_instance,
            context.task.id,
            self.AGENT_TYPE,
            context.task.headers,
            context.task.input.as_dict(),
        )

        try:
            # check required headers
            assert job.headers is not None
            assert "arguments" in job.headers, "'arguments' custom header missing"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # RUN BASH APPLICATION
            self.application_python_handler(job)
        except Exception as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        # send success status to jobs tracking
        self.jobs.update(job, status=STATUS_COMPLETE, end_at=datetime.now())

    def application_python_handler(self, job: Job):
        """
        Run python application

        :param job: Job instance
        :return:
        """
        if job.headers is None:
            return

        # get command arguments template
        template = jinja2.Template(job.headers["arguments"])
        arguments = template.render(job.input)

        application = self.applications.run(
            job,
            self.APPLICATIONS["python"].name,
            self.APPLICATIONS["python"].version
            if "applications.python.version" not in job.headers
            else job.headers["applications.python.version"],
            f"python {arguments}",
        )

        if application.status == APPLICATION_STATUS_ABORTED:
            raise ApplicationAborted(
                f"Application {application.name} ({application.id}) aborted"
            )
        if application.status != APPLICATION_STATUS_COMPLETE:
            raise ApplicationError(
                application.container_error
                if application.container_error
                else "Application command error, see application logs"
            )
