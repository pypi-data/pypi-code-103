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
Madam scanfolder agent module
"""
import json
from datetime import datetime
from pathlib import Path

import adhesive
import jinja2

from madam.adapters.interfaces.agents import AdhesiveAgentInterface
from madam.domains.entities.job import STATUS_COMPLETE, STATUS_ERROR
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.jobs import Jobs
from madam.libs.serialize import WorkflowInstanceJSONDecoder


class AdhesiveScanfolderAgent(AdhesiveAgentInterface):
    """
    AdhesiveScanfolderAgent class
    """

    AGENT_TYPE = "scanfolder"

    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs) -> None:
        """
        Init AdhesiveScanfolderAgent with domains

        :param jobs: Jobs domain instance
        """
        self.jobs = jobs

    def execute(self, context: adhesive.ExecutionToken) -> None:
        """
        Execute a scan of a folder and return a list of files

        Input Variables:
            source: string with absolute path of the folder to scan

        Output Variables:
            items: list of string of item paths in the folder

        Headers:
            recursive: string ("true" or "false") scan folder recursively if "true"
            glob_[your suffix]: Optional[string] glob pattern to filter items

        Example: glob_mp4 = "*.mp4"
                 glob_video = "video_*.*"

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
            assert Path(
                job.input["source"]
            ).exists(), f"source path '{job.input['source']}' does not exist"
            assert Path(
                job.input["source"]
            ).is_dir(), f"source path '{job.input['source']}' is not a directory"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        try:
            # check required headers
            assert job.headers is not None
            assert "recursive" in job.headers, "'recursive' custom header missing"
        except AssertionError as exception:
            # send error status to jobs tracking
            self.jobs.update(
                job, status=STATUS_ERROR, error=str(exception), end_at=datetime.now()
            )
            # stop workflow instance
            raise exception

        # set recursive as boolean
        recursive_mode = context.task.headers["recursive"].lower() == "true"
        # get glob_* options
        glob_dict = dict(
            filter(
                lambda items: items[0].startswith("glob_"), context.task.headers.items()
            )
        )

        # scan source
        paths = []
        # if no glob_* options...
        if len(glob_dict) == 0:
            paths = [
                str(path)
                for path in (
                    Path(context.task.input.source).rglob("*")
                    if recursive_mode is True
                    else Path(context.task.input.source).glob("*")
                )
                if Path(path).is_file()
            ]
        else:
            for pattern in glob_dict.values():

                # parse jinja2 tags
                template = jinja2.Template(pattern)
                pattern = template.render(job.input)

                if recursive_mode is True:
                    # use glob pattern source folder path
                    paths += [
                        str(path)
                        for path in Path(context.task.input.source).rglob(pattern)
                        if Path(path).is_file()
                    ]
                else:
                    # use glob pattern source folder path
                    paths += [
                        str(path)
                        for path in Path(context.task.input.source).glob(pattern)
                        if Path(path).is_file()
                    ]

        # output variables
        context.task.output.items = paths

        # send success status to jobs tracking
        self.jobs.update(
            job,
            status=STATUS_COMPLETE,
            end_at=datetime.now(),
            output=context.task.output.as_dict(),
        )
