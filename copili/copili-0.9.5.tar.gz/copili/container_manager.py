import os
import sys
import docker
import logging
import time
import json
import threading
from docker.client import DockerClient
from linetimer import CodeTimer
from .registry import ContainerRegistryItem
from typing import Dict, List


class ContainerManager:
    exit_code: int = None
    run_time: float = None
    skipped: bool = None
    canceled: bool = None
    container_desc: ContainerRegistryItem = None
    image: docker.models.images.Image = None
    container: docker.models.containers.Container = None
    sidecars: List["ContainerManager"] = None
    log_handler: logging.Logger = None

    def __init__(
        self,
        docker_client: docker.DockerClient,
        container_desc: ContainerRegistryItem,
        force_repull: bool = True,
        log_to_seperate_file: bool = True,
        log_path: str = None,
    ):
        self.log = logging.getLogger(container_desc.name)
        self.docker_client = docker_client
        self.container_desc = container_desc
        self.force_repull = force_repull
        self.setup_logger(log_to_seperate_file, log_path)
        self.run_time: int = 0
        self.sidecars: List["ContainerManager"] = [
            self.__class__(
                docker_client=docker_client,
                container_desc=sidecar_desc,
                force_repull=force_repull,
                log_to_seperate_file=False,
            )
            for sidecar_desc in container_desc.sidecars
        ]
        self.sidecar_log_threads: List[threading.Thread] = []

    def setup_logger(self, log_to_seperate_file: bool, log_path: str):
        if log_to_seperate_file:
            if log_path is None:
                main_dir = os.path.dirname(
                    os.path.abspath(sys.modules["__main__"].__file__)
                )
                log_path = os.path.join(main_dir, "logs")
            try:
                os.makedirs(log_path)
            except FileExistsError:
                pass

            self.log_handler = logging.FileHandler(
                os.path.join(log_path, "{}.log".format(self.container_desc.name))
            )
            self.log.addHandler(self.log_handler)

    def pull(self):
        self.log.info(
            "Try to pull image '{}' ...".format(self.container_desc.image_repo)
        )
        if self.force_repull:
            self.log.info("... pull is forced; try to removing existing image ...")
            try:
                self.docker_client.images.remove(
                    "{}:{}".format(
                        self.container_desc.image_repo, self.container_desc.tag
                    )
                )
                self.log.info("... image removed ...")
            except docker.errors.ImageNotFound:
                self.log.info("... image not present ...")
                pass
        pull_params = {}
        pull_params["repository"] = self.container_desc.image_repo
        pull_params["tag"] = self.container_desc.tag

        if (
            self.container_desc.image_reg_password is not None
            and self.container_desc.image_reg_username is not None
        ):
            pull_params["auth_config"] = {
                "username": self.container_desc.image_reg_username,
                "password": self.container_desc.image_reg_password,
            }
        self.log.debug("PULL PARAMS:\n{}".format(json.dumps(pull_params, indent=4)))
        self.image = self.docker_client.images.pull(**pull_params)
        self.log.info(
            "...image '{}' pulled.".format(
                "{}:{}".format(self.container_desc.image_repo, self.container_desc.tag)
            )
        )

    def clean_up(self):
        if self.container is not None:
            # clean up sidecars first
            for sidecar in self.sidecars:
                sidecar.clean_up()

            try:
                c = self.container
                self.log.info("Clean up {}".format(self.container_desc.name))
                try:
                    c.kill()
                except docker.errors.APIError:
                    pass
                try:
                    c.remove()
                except docker.errors.APIError:
                    pass
            except docker.errors.NotFound:
                pass
            self.log.info(
                "Stopped and removed container {} - {}:{}".format(
                    self.container_desc.name,
                    self.container_desc.image_repo,
                    self.container_desc.tag,
                )
            )
            if self.log_handler:
                logging.getLogger().removeHandler(self.log_handler)
            # clean up sidecar log threads
            for sidecar_log_thread in self.sidecar_log_threads:
                sidecar_log_thread.join()

    def run(
        self,
        pull=True,
        extra_envs: Dict = None,
        network_mode="bridge",
        background=False,
    ):
        timer = CodeTimer(name=self.container_desc.name, silent=True, unit="s")
        # start sidecars

        for sidecar in self.sidecars:
            self.log.info(f"Start sidecar {sidecar.container_desc.name}")
            sidecar.run(
                pull=pull,
                extra_envs=extra_envs,
                network_mode=network_mode,
                background=True,
            )
        self.log_sidecars()

        if extra_envs is None:
            extra_envs = {}
        with timer:
            if pull:
                self.pull()
            self.log.info(
                "Starting container {} from image {}:{}".format(
                    self.container_desc.name,
                    self.container_desc.image_repo,
                    self.container_desc.tag,
                )
            )
            self.container = self.docker_client.containers.run(
                image="{}:{}".format(
                    self.container_desc.image_repo, self.container_desc.tag
                ),
                environment=self.container_desc.get_env_vars(extra_envs),
                detach=True,
                name=self.container_desc.name,
                volumes=self.container_desc.volumes,
                auto_remove=False,  # Autoremove will prevent us from reliable getting the exit code at the end. we need to remove the container manualy
                command=[str(val) for val in self.container_desc.command],
                network_mode=network_mode,
            )
            if not background:
                self.recieve_logs()
                try:
                    time.sleep(1)
                    res = self.container.wait()
                except Exception as error:
                    self.log.error(error)
                    # edge case fix; some race condition or whatever. wait() fails
                    self.log.warning("Could not determine exit code. Default to 0")

                    res = {"Error": "None", "StatusCode": 0}
        if not background:
            self.exit_code = res["StatusCode"]
            self.run_time = timer.took

            self.clean_up()

    def recieve_logs(self):
        try:
            for l in self.container.logs(
                stream=True,
                timestamps=True,
                follow=True,
                stderr=True,
                stdout=True,
            ):
                self.log.info(l.decode())
        except (docker.errors.NotFound, docker.errors.APIError) as e:
            # Edge cases; container exited faster then we could attach.
            # this happens for example with debug/demo containers like "hello-world" with virtually no runtime
            # there where some weird docker.errors.APIError ~"409 Client Error: Conflict" cases...could not reproduce. revisit if necessary
            if type(e) == docker.errors.NotFound:
                self.log.info(
                    f"{prefix}No logs for container {self.container_desc.name}"
                )
            else:
                raise e

    def log_sidecars(self):
        for sidecar in self.sidecars:
            log_thread = threading.Thread(
                target=sidecar.recieve_logs,
                args=(),
            )
            log_thread.daemon = True
            log_thread.start()
            self.sidecar_log_threads.append(log_thread)
