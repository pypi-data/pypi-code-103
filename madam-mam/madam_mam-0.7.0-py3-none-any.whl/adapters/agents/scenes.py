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
Madam scenes agent module
"""
import json
import re
from datetime import datetime

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
    Application,
    ApplicationAborted,
    ApplicationError,
)
from madam.domains.entities.job import STATUS_COMPLETE, STATUS_ERROR, Job
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.jobs import Jobs
from madam.libs.serialize import WorkflowInstanceJSONDecoder
from madam.libs.timecode import TimecodeSeconds


class AdhesiveScenesAgent(AdhesiveApplicationAgentInterface):
    """
    AdhesiveScenesAgent class
    """

    AGENT_TYPE = "scenes"
    APPLICATIONS = {"ffmpeg": AgentApplication("ffmpeg", "latest")}

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs, applications: Applications) -> None:
        """
        Init AdhesiveScenesAgent with domains

        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        self.jobs = jobs
        self.applications = applications

    def execute(self, context: adhesive.ExecutionToken) -> None:
        """
        Get a list of the scenes (shots) of the video from the path provided

        Input Variables:
            source: string of the source video path

        Output Variables:
            scenes: list of dictionaries with scene informations

                    {
                        "index": int,  # int with scene index number
                        "start": str,  # Start timecode in second format like 00:00:00:00.000
                        "end": str,  # End timecode in second format like 00:00:00:00.000
                        "duration": str,  # Duration timecode in second format like 00:00:00:00.000
                    }

        Headers:
            diff: Optional[float] of the sensibility level of the detection (default=0.4)

            applications.ffmpeg.version: Optional[string] with version for ffmpeg label application

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
            assert "source" in job.input, "'source' variable missing"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # RUN FFMPEG APPLICATION
            application = self.application_ffmpeg_handler(job)
        except Exception as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        # capture list of scenes from logs
        scenes_ = []
        count = 0
        last_start = float(0)
        duration = float(0)
        regex_duration = re.compile(r"Duration: (\d{2}):(\d{2}):(\d+\.\d+)")
        regex_pts_time = re.compile(r"pts_time:(\d+\.\d+)")
        for line in application.logs.split("\n"):  # type: ignore
            match_pts_time = regex_pts_time.search(line)
            if match_pts_time:
                # capture scene cut in seconds
                cut = float(match_pts_time.groups()[0])

                scenes_.append(
                    {
                        "index": count,
                        "start": str(TimecodeSeconds(last_start)),
                        "end": str(TimecodeSeconds(cut)),
                        "duration": str(TimecodeSeconds(cut - last_start)),
                    }
                )
                count += 1
                last_start = cut
            else:
                match_duration = regex_duration.search(line)
                if match_duration:
                    hours, minutes, seconds = match_duration.groups()
                    duration = float(
                        (int(hours) * 3600) + (int(minutes) * 60) + float(seconds)
                    )

        # the last or the only scene
        scenes_.append(
            {
                "index": count,
                "start": str(TimecodeSeconds(last_start)),
                "end": str(TimecodeSeconds(duration)),
                "duration": str(TimecodeSeconds(duration - last_start)),
            }
        )

        # output variables
        context.task.output.scenes = scenes_

        # send success status to jobs tracking
        self.jobs.update(
            job,
            status=STATUS_COMPLETE,
            output=context.task.output.as_dict(),
            end_at=datetime.now(),
        )

    def application_ffmpeg_handler(self, job: Job) -> Application:
        """
        Run ffmpeg application

        :param job: Job instance
        :return:
        """
        diff = (
            job.headers["diff"]
            if job.headers is not None and "diff" in job.headers
            else 0.4
        )
        arguments = f"-i {job.input['source']} -filter:v \"select='gt(scene,{diff})',showinfo\" -f null -"

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

        if application.logs is None:
            raise ApplicationError(
                application.container_error
                if application.container_error
                else f"Application {application.name} ({application.id}) log is empty, can not get scenes"
            )

        return application
