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

import logging
from typing import Optional

from docker.errors import NotFound

from madam.adapters.process import docker_api
from madam.domains.entities.application import (
    STATUS_ABORTED,
    STATUS_COMPLETE,
    STATUS_CONTAINER_ERROR,
    STATUS_ERROR,
    Application,
)
from madam.domains.interfaces.process.applications import (
    ApplicationProcessManagerInterface,
)
from madam.domains.interfaces.repository.config import ConfigRepositoryInterface


class DockerApplicationProcessManager(ApplicationProcessManagerInterface):
    """
    DockerApplicationProcess
    """

    def __init__(self, config: ConfigRepositoryInterface) -> None:
        """
        Init DockerApplicationProcessManager instance with ConfigRepositoryInterface instance

        :param config: ConfigRepositoryInterface instance
        :return:
        """
        self.config = config.get_root_key("docker")

    def run(self, application: Application, config: Optional[dict] = None):
        if ApplicationProcessManagerInterface.run.__doc__ is not None:
            __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
                ApplicationProcessManagerInterface.run.__doc__
                + """
                config parameters for Docker:
                
                mounts: List[str]
                    List of mounts to add to madam configuration
                command: str
                    Command to override default docker service command (image entrypoint)
                init: bool
                    Run an init inside the container that forwards signals and reaps processes (default=False)
                """
            )

        # container options
        image = self.config["applications"][application.name][application.version]

        if config is not None:
            # merge config mounts with dynamically added mounts
            if "mounts" not in config:
                mounts = self.config["mounts"]
            else:
                mounts = self.config["mounts"] + config["mounts"]
            command = None if "command" not in config else config["command"]
            init = bool("init" in config and config["init"] is True)
        else:
            # docker service config defaults
            mounts = self.config["mounts"]
            command = None
            init = False

        container_labels = {
            "madam.workflow.id": str(application.job.workflow_instance.workflow.id),
            "madam.application": application.name,
            "madam.job.id": str(application.job.id),
        }

        # run application in container
        service = docker_api.run_service(
            self.config["base_url"],
            image,
            mounts,
            command,
            application.arguments,
            application.container_name,
            container_labels,
            self.config["networks"],
            init,
        )
        application.container_id = service.id

    def wait(self, application: Application, ignore_failure: bool = False) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationProcessManagerInterface.wait.__doc__
        )
        if application.container_id is None:
            return

        try:
            # capture service from process ID
            service = docker_api.get_service(
                self.config["base_url"], application.container_id
            )
        except NotFound as exception:
            logging.exception(exception)
            return

        # wait end of service
        status = docker_api.wait_service(service)

        if status == docker_api.DOCKER_TASK_STATE_REJECTED:
            # capture container error
            tasks = service.tasks()
            application.status = STATUS_CONTAINER_ERROR
            application.container_error = tasks[0]["Status"]["Err"]

        elif status == docker_api.DOCKER_TASK_STATE_FAILED and ignore_failure is False:
            tasks = service.tasks()
            container_error = None
            if tasks[0]["Status"]["Err"] is not None:
                # capture container error
                container_error = tasks[0]["Status"]["Err"]
            # capture application logs
            logs = "\n".join(
                [
                    line.decode("utf-8")
                    for line in service.logs(stderr=True, stdout=True)
                ]
            )
            application.status = STATUS_ERROR
            application.container_error = container_error
            application.logs = logs

        elif status == docker_api.DOCKER_SERVICE_ABORTED:
            application.status = STATUS_ABORTED

        else:
            # capture application logs and save it in Application
            logs = "\n".join(
                [
                    line.decode("utf-8")
                    for line in service.logs(stderr=True, stdout=True)
                ]
            )
            application.status = STATUS_COMPLETE
            application.logs = logs

    def delete_container(self, id: str) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationProcessManagerInterface.delete_container.__doc__
        )
        try:
            # capture service from process ID
            service = docker_api.get_service(self.config["base_url"], id)
        except NotFound:
            logging.warning("delete container ID=%s error: container not found", id)
            return

        service.remove()

    def abort_container(self, id: str) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ApplicationProcessManagerInterface.abort_container.__doc__
        )
        try:
            # capture service from container ID
            service = docker_api.get_service(self.config["base_url"], id)
        except NotFound:
            logging.warning("abort container ID=%s error: container not found", id)
            return

        if service is None:
            return

        # stop the service tasks by scaling it to 0 replica
        service.scale(0)
