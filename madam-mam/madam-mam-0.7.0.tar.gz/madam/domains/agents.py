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

import importlib
import inspect
import pkgutil
from typing import List, Optional, Union

from madam.adapters import agents
from madam.domains.entities.agent import Agent
from madam.domains.interfaces.repository.config import ConfigRepositoryInterface


class Agents:
    """
    Madam Agents domain class
    """

    def __init__(self, config: ConfigRepositoryInterface):
        """
        Init Agents instance with ConfigRepositoryInterface dependency

        :param config: ConfigRepositoryInterface instance
        """
        self.config = config
        self.check_config()

    def check_config(self):
        """
        Check if config repository contains application versions used in agents

        :return:
        """
        docker_config = self.config.get_root_key("docker")
        docker_applications_config = docker_config["applications"]
        for agent in self.list():  # type: Agent
            if agent.applications is not None:
                for _, agent_application in agent.applications.items():
                    if agent_application.name not in docker_applications_config:
                        raise AgentApplicationNotFoundInConfig(
                            f"docker.applications.{agent_application.name} not found in config"
                        )
                    if (
                        agent_application.version
                        not in docker_applications_config[agent_application.name]
                    ):
                        raise AgentApplicationVersionNotFoundInConfig(
                            f"docker.applications.{agent_application.name}.{agent_application.version} not found in "
                            f"config"
                        )

    def read(self, name: str) -> Optional[Agent]:
        """
        Return an Agent object by its module name

        :param name: Agent's module name
        :return:
        """
        return self._get_agent_from_module_name(name)

    def list(self, only_names: bool = False) -> Union[List[str], List[Agent]]:
        """
        Return a list of available agent names if only_names is True
        Return a list of Agent objects otherwise

        :param only_names: Return a list of names if True (default=False)

        :return:
        """
        modules = [
            modname
            for _, modname, ispkg in pkgutil.iter_modules(agents.__path__)  # type: ignore  # mypy issue #1422
            if not ispkg
        ]
        if only_names is True:
            return modules

        agents_ = []
        for name in modules:
            agent = self._get_agent_from_module_name(name)
            if agent is not None:
                agents_.append(agent)

        return agents_

    @staticmethod
    def _get_agent_from_module_name(name: str) -> Optional[Agent]:
        """
        Return an Agent object from the agent module's name

        :param name: Agent module's name
        :return:
        """
        # get agent class from module
        module_reference_path = f"{agents.__package__}.{name}"
        module = importlib.import_module(module_reference_path)
        for module_attribute_name in dir(module):
            module_attribute = getattr(module, module_attribute_name)
            # capture the only class defined in the module
            if (
                inspect.isclass(module_attribute)
                and module_attribute.__module__ == module_reference_path
            ):
                help_ = module_attribute.execute.__doc__
                applications = (
                    None
                    if not hasattr(module_attribute, "APPLICATIONS")
                    else module_attribute.APPLICATIONS
                )
                return Agent(name=name, help=help_, applications=applications)

        return None


class AgentApplicationNotFoundInConfig(Exception):
    """
    AgentApplicationConfigNotFound exception class
    """


class AgentApplicationVersionNotFoundInConfig(Exception):
    """
    AgentApplicationVersionNotFoundInConfig exception class
    """
