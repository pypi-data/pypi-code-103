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
Madam concatenate agent module
"""
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import adhesive

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
CONCATENATE_PLAYLIST_PATH = "/tmp"


class AdhesiveConcatenateAgent(AdhesiveApplicationAgentInterface):
    """
    AdhesiveConcatenateAgent class
    """

    AGENT_TYPE = "concatenate"
    APPLICATIONS = {"ffmpeg": AgentApplication("ffmpeg", "latest")}

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs, applications: Applications) -> None:
        """
        Init AdhesiveBashAgent with domains

        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        self.jobs = jobs
        self.applications = applications

    def execute(self, context: adhesive.ExecutionToken) -> None:
        """
        Concatenate a list of media sources into a destination file

        Input Variables:
            sources: list of string of the source paths
            destination: string path of the destination file

        Headers:
            applications.ffmpeg.version: Optional[string] with version for ffmpeg label application

        Note : need to create a temporary playlist file from sources list in the destination directory

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
            # check required variables
            assert job.input is not None
            assert "sources" in job.input, "'sources' variable missing"
            assert "destination" in job.input, "'destination' variable missing"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # create a playlist file from the sources, in the destination directory
            fd, playlist_fullpath = tempfile.mkstemp(
                dir=Path(
                    job.input["destination"], prefix="madam_concatenate_playlist_"
                ).parent
            )
            with open(playlist_fullpath, "w", encoding="utf-8") as fh:
                for source_path in context.task.input.sources:
                    fh.write(f"file {source_path}\n")
            # close the file descriptor
            os.close(fd)
            # required when in dev environment as dev user != docker user...
            old_umask = os.umask(0o000)
            os.chmod(playlist_fullpath, 0o777)
            os.umask(old_umask)
        except Exception as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # RUN FFMPEG APPLICATION
            self.application_ffmpeg_handler(job, playlist_fullpath)
        except Exception as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        # output variables
        context.task.output.destination = context.task.input.destination
        # send success status to jobs tracking
        self.jobs.update(
            job,
            status=STATUS_COMPLETE,
            output=context.task.output.as_dict(),
            end_at=datetime.now(),
        )

        if Path(playlist_fullpath).exists():
            try:
                # remove playlist file
                os.unlink(playlist_fullpath)
            except Exception as exception:
                logging.exception(exception)

    def application_ffmpeg_handler(self, job: Job, playlist_path: str) -> None:
        """
        Run ffmpeg application

        :param job: Job instance
        :param playlist_path: Path of the playlist file
        :return:
        """
        arguments = (
            f'-y -f concat -safe 0 -i "{playlist_path}" "{job.input["destination"]}"'
        )
        # mount playlist_path in application container
        application = self.applications.run(
            job,
            self.APPLICATIONS["ffmpeg"].name,
            self.APPLICATIONS["ffmpeg"].version
            if job.headers is None
            else job.headers.get(
                "applications.ffmpeg.version", self.APPLICATIONS["ffmpeg"].version
            ),
            arguments,
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
