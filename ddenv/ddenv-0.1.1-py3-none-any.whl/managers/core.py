from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Optional, Type

from docker import from_env
from docker.models.containers import Container


class BaseManager(ABC):
    def __init__(self, version: Optional[str], workdir: str):
        self._version = version
        self._workdir = workdir
        self.docker_client = from_env()

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the manager"""

    @property
    def version(self) -> str:
        """Returns the version"""
        return self._version

    @property
    def workdir(self) -> str:
        """Return the current workdir"""
        return self._workdir

    def workdir_file(self, file: str) -> Path:
        """Get the path to a file in the current workdir"""
        return Path(self.workdir, file)

    @property
    @abstractmethod
    def image_name(self) -> str:
        """Return the name of the image"""
        return "ddenv"

    @property
    @abstractmethod
    def image_tag(self) -> str:
        """Returns the tag of the image"""

    @property
    @abstractmethod
    def image_exists(self) -> bool:
        """Check whether the base image already exists"""

    @abstractmethod
    def build_base_image(self):
        """
        Build the base image used for running commands.
        Should include all dependencies.
        """

    @abstractmethod
    def run_command(
        self, command: Optional[list[str]], ports: Optional[list[str]]
    ) -> Container:
        """Run the given command in the base image and return the logs"""


class ManagerNotFoundError(Exception):
    pass


def find_manager_mod(name: str) -> ModuleType:
    try:
        return import_module(f"ddenv.managers.{name}.manager")
    except ModuleNotFoundError:
        raise ValueError(f"Manager {name} not found")


def find_manager(name: str) -> Type[BaseManager]:
    manager_mod = find_manager_mod(name)

    try:
        return manager_mod.__dict__["Manager"]
    except KeyError:
        raise ManagerNotFoundError(
            f"`Manager(BaseManager)` class not found in {manager_mod.__name__}"
        )


def get_manager(name: str, version: str, workdir: str) -> BaseManager:
    return find_manager(name)(version, workdir)
