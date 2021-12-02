from .container_manager import ContainerManager
from .registry import ContainerRegistryItem
from .registry import ContainerRegistry
import os
import sys
import logging
import docker
import time
import schedule
import atexit
import signal
from linetimer import CodeTimer
from typing import List, Dict, Callable


log = logging.getLogger(__name__)


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )

    sys.path.append(os.path.normpath(SCRIPT_DIR))


class Pipeline:
    registry: ContainerRegistry = None
    global_env_vars: Dict = None
    container_pre_pull_callback: Callable = None
    container_pre_run_callback: Callable = None
    container_post_run_callback: Callable = None
    container_did_run_check_override_callback: Callable = None
    container_dependency_check_override_callback: Callable = None
    container_log_path: str = None
    container_force_image_pull: bool = None
    service_schedule = None
    network_mode = "bridge"

    def __init__(
        self,
        description: str,
        docker_client: docker.DockerClient = None,
        dot_env_path: str = "./.env",
    ):
        """[summary]

        Args:
            description (str): path to yaml or json file or yaml or json string. List of container descriptions
        """
        if docker_client is None:
            self.docker_client = docker.DockerClient(
                base_url="unix://var/run/docker.sock"
            )
        else:
            self.docker_client = docker_client
        self.container_force_image_pull = False
        self.registry: ContainerRegistry = ContainerRegistry(description, dot_env_path)
        self.container_managers: List[ContainerManager] = []
        self.running_container_managers: List[ContainerManager] = []
        self.finished_container_managers: List[ContainerManager] = []
        self.global_env_vars = {}
        atexit.register(self._atexit)
        signal.signal(signal.SIGTERM, self._atexit)
        signal.signal(signal.SIGINT, self._atexit)

    def _atexit(self):
        for container_manager in self.running_container_managers:
            container_manager.clean_up()

    def add_global_env_var(self, key, value):
        self.global_env_vars[key] = value

    def _container_depenencies_did_run_check(self, container_manager: ContainerManager):
        log.info(
            "Check dependencies for {}:".format(container_manager.container_desc.name)
        )
        if callable(self.container_dependency_check_override_callback):
            return self.container_dependency_check_override_callback(
                container_manager,
                self.finished_container_managers,
            )
        else:
            # default dependency check
            successfully_run_reg_item_names = [
                manag.container_desc.name
                for manag in self.finished_container_managers
                if manag.exit_code == 0
            ]

            for reg_item_dep in container_manager.container_desc.dependencies:
                if reg_item_dep not in successfully_run_reg_item_names:
                    return False
        return True

    def _container_did_already_run_check(self, container_manager: ContainerManager):
        # custom caller check
        if callable(self.container_did_run_check_override_callback):
            return self.container_did_run_check_override_callback(
                container_manager, self.finished_container_managers
            )
        else:
            return False

    def _run(self, container_descs: List[ContainerRegistryItem]):
        for container_desc in container_descs:
            skip_or_cancel = False
            container_manager = ContainerManager(
                docker_client=self.docker_client,
                container_desc=container_desc,
                log_path=self.container_log_path,
                force_repull=self.container_force_image_pull,
            )
            self.container_managers.append(container_manager)
            self.running_container_managers.append(container_manager)

            if callable(self.container_pre_pull_callback):
                self.container_pre_pull_callback(container_manager)
            container_manager.pull()

            # skip running container if caller set a skip check function which returns 'True' and container is not a service container
            if (
                not container_desc.is_service_container
                and self._container_did_already_run_check(container_manager)
            ):
                container_manager.exit_code = 0
                container_manager.skipped = True
                log.info(
                    "Skip {} because it did allready run.".format(
                        container_desc.name, ",".join(container_desc.dependencies)
                    )
                )
                skip_or_cancel = True
            else:
                container_manager.skipped = False

            if not self._container_depenencies_did_run_check(container_manager):
                container_manager.exit_code = 1
                container_manager.canceled = True
                log.error(
                    "Can not start {} because of missing dependency (dependecies: {})".format(
                        container_desc.name, ",".join(container_desc.dependencies)
                    )
                )
                skip_or_cancel = True
            else:
                container_manager.canceled = False
            if not skip_or_cancel:
                if callable(self.container_pre_run_callback):
                    self.container_pre_run_callback(container_manager)

                # RUN main container
                container_manager.run(
                    pull=False,
                    extra_envs=self.global_env_vars,
                    network_mode=self.network_mode,
                )
                if callable(self.container_post_run_callback):
                    self.container_post_run_callback(container_manager)
            self.running_container_managers.remove(container_manager)
            self.finished_container_managers.append(container_manager)
            container_manager.log.info("========================================")
            container_manager.log.info(
                "FAILED: {}".format(
                    "False" if container_manager.exit_code == 0 else "True"
                )
            )
            container_manager.log.info(
                "EXITED with status: {}".format(container_manager.exit_code)
            )

            container_manager.log.info("SKIPPED: {}".format(container_manager.skipped))
            container_manager.log.info(
                "CANCELED: {}".format(container_manager.canceled)
            )
            container_manager.log.info(
                "RUNTIME: {} minutes".format(container_manager.run_time / 60)
            )
            container_manager.log.info("========================================")
            container_manager.log.info("")

    def run(self):
        log.info("=====Start '{}'======".format(self.registry.name))
        self._run(self.registry.get_ordered_containers())

    def run_service_containers(self):
        self._run(self.registry.get_ordered_containers(service_containers_only=True))

    def start_service_mode(self):
        log.info("========START SERVICE MODE===========")
        if self.service_schedule is None:
            self.service_schedule = (
                schedule.every().day.at("00:00").do(self.run_service_containers)
            )
            log.info(
                "No service schedule set by caller. Use default schedule:\n\t{}".format(
                    self.service_schedule
                )
            )
        while True:
            schedule.run_pending()
            time.sleep(1)
