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
Madam imagemagick agent module
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

# agent constants
APPLICATION_IMAGEMAGICK_COMMANDS = [
    "magick",
    "magick-script",
    "compare",
    "composite",
    "conjure",
    "convert",
    "identify",
    "mogrify",
    "montage",
]


class AdhesiveImageMagickAgent(AdhesiveApplicationAgentInterface):
    """
    AdhesiveImageMagickAgent class
    """

    AGENT_TYPE = "imagemagick"
    APPLICATIONS = {"imagemagick": AgentApplication("imagemagick", "latest")}

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs, applications: Applications) -> None:
        """
        Init AdhesiveImageMagickAgent with domains

        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        self.jobs = jobs
        self.applications = applications

    def execute(self, context: adhesive.ExecutionToken) -> None:
        """
        Execute ImageMagick commands with arguments provided

        Headers:
            command:    string with ImageMagick command to use
                        Supported commands are:
                        - magick
                        - magick-script
                        - compare
                        - composite
                        - conjure
                        - convert
                        - identify
                        - mogrify
                        - montage

            arguments:  string with ImageMagick arguments parsed as a jinja2 string
                        (workflow variables can be used with jinja2 tags, see https://jinja.palletsprojects.com/en/3.0.x/templates/#variables)

            applications.imagemagick.version: Optional[string] with version for imagemagick label application

        Example: arguments = "-size 100x100 {{source}} {{destination}}"

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
            assert "command" in job.headers, "'command' custom header missing"
            assert (
                job.headers["command"] in APPLICATION_IMAGEMAGICK_COMMANDS
            ), f"command {job.headers['command']} not supported"
            assert "arguments" in job.headers, "'arguments' custom header missing"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # RUN IMAGEMAGICK APPLICATION
            self.application_imagemagick_handler(job)
        except Exception as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        # send success status to jobs tracking
        self.jobs.update(job, status=STATUS_COMPLETE, end_at=datetime.now())

    def application_imagemagick_handler(self, job: Job):
        """
        Run imagemagick application

        :param job: Job instance
        :return:
        """
        if job.headers is None:
            return

        # get command arguments template
        template = jinja2.Template(job.headers["arguments"])
        arguments = template.render(job.input)

        # ImageMagick docker image utility name is set in command parameter (entrypoint)
        docker_config = {"command": job.headers["command"]}

        application = self.applications.run(
            job,
            self.APPLICATIONS["imagemagick"].name,
            self.APPLICATIONS["imagemagick"].version
            if "applications.imagemagick.version" not in job.headers
            else job.headers["applications.imagemagick.version"],
            arguments,
            docker_config,
            ignore_failure=job.headers["command"] == "compare",
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
