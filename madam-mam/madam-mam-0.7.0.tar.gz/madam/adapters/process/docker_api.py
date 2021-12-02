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
Madam docker_api module
"""
import logging
import shlex
from time import sleep, time
from typing import Optional

from docker.models.services import Service

from docker import DockerClient, types

DOCKER_TASK_STATE_COMPLETE = "complete"
DOCKER_TASK_STATE_FAILED = "failed"
DOCKER_TASK_STATE_REJECTED = "rejected"
DOCKER_SERVICE_ABORTED = "aborted"

WAIT_FOR_TASK_TO_START_TIMEOUT = 30
WAIT_FOR_TASK_TO_END_TIMEOUT = 3600 * 12


def run_service(
    docker_url: str,
    image: str,
    mounts: list,
    command: Optional[str],
    arguments: str,
    name: str,
    container_labels: dict,
    networks: Optional[list],
    init: bool = False,
) -> Service:
    """
    Run docker service in container and return Service instance if successful, None otherwise

    :param docker_url: Url to docker API
    :param image: Name of image
    :param mounts: List of docker mounts
    :param command: Command to run in the container
    :param arguments: Arguments to give to the container
    :param name: Name of the container (for logging)
    :param container_labels: Labels to set on container
    :param networks: List of docker networks name|ID
    :param init: Run an init inside the container that forwards signals and reaps processes (default=False)

    :return:
    """
    # init docker api client on swarm manager host
    docker_client = DockerClient(docker_url)

    # debug
    # services = docker_client.services.list()
    # for service in services:
    #     service.remove()

    # create and run service on docker swarm
    service = docker_client.services.create(
        name=name,
        image=image,
        command=command,
        args=shlex.split(arguments),
        mounts=mounts,
        restart_policy=types.RestartPolicy(),  # Default=None
        labels=container_labels,
        networks=networks,
        init=init,
    )
    if service is not None:
        logging.info("container %s started", service.name)

    return service


def wait_service(service: Service, timeout: int = WAIT_FOR_TASK_TO_END_TIMEOUT) -> str:
    """
    Wait for a docker service to exit, and return task status state string

    :param service: Docker Service instance
    :param timeout: Timeout of the application in seconds (default=3600 * 12)
    :return:
    """
    # wait for the task to start...
    start_time = time()
    while len(service.tasks()) == 0:
        sleep(1)
        if time() > start_time + WAIT_FOR_TASK_TO_START_TIMEOUT:
            logging.error("wait service id=%s with no task timeout", service.id)
            return DOCKER_TASK_STATE_FAILED

    # wait for end of service task
    start_time = time()
    status = ""
    while time() < start_time + timeout:
        sleep(1)
        try:
            tasks = service.tasks()
        except Exception as exception:
            logging.error("polling service %s error: %s", service.name, exception)
            continue

        # if task not ready yet...
        if len(tasks) < 1:
            logging.warning("service id=%s aborted!", service.id)
            return DOCKER_SERVICE_ABORTED

        # if task complete...
        if (
            tasks[0]["Status"]["State"] == DOCKER_TASK_STATE_COMPLETE
            or tasks[0]["Status"]["State"] == DOCKER_TASK_STATE_FAILED
            or tasks[0]["Status"]["State"] == DOCKER_TASK_STATE_REJECTED
        ):
            status = tasks[0]["Status"]["State"]
            logging.info("service %s task status %s", service.name, status)
            break

    return status


def remove_service(service: Service, application_name: str) -> bool:
    """
    Remove container of service

    :param service: Service instance
    :param application_name: Name of application for logging
    :return:
    """
    try:
        service.remove()
    except Exception as exception:
        logging.error(
            "application %s delete container %s error: %s",
            application_name,
            service.name,
            exception,
        )
        return False

    logging.info(
        "application %s in container %s removed", application_name, service.name
    )
    return True


def get_service(docker_url: str, service_id: str) -> Service:
    """
    Get docker service instance from service_id

    :param docker_url: Url to docker daemon
    :param service_id: Id of service
    :return:
    """
    # init docker api client on swarm manager host
    docker_client = DockerClient(docker_url)

    # debug
    # services = docker_client.services.list()
    # for service in services:
    #     service.remove()

    # create and run service on docker swarm
    service = docker_client.services.get(service_id)

    return service
