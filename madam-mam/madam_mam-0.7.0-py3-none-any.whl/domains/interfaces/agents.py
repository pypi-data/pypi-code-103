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

import abc

from madam.domains.applications import Applications
from madam.domains.jobs import Jobs


class AgentInterface(abc.ABC):
    """
    Agent domain interface
    """

    @property
    @classmethod
    @abc.abstractmethod
    def AGENT_TYPE(cls) -> str:
        """
        AGENT_TYPE required property
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __init__(self, jobs: Jobs):
        """
        Init Agent instance with Jobs domain instance

        :param jobs: Jobs domain instance
        """
        raise NotImplementedError


class ApplicationAgentInterface(AgentInterface):
    """
    ApplicationAgent domain interface
    """

    @property
    @classmethod
    @abc.abstractmethod
    def APPLICATIONS(cls) -> dict:
        """
        APPLICATIONS required property
        Dict with application name as key and version as value

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(self, jobs: Jobs, applications: Applications):
        """
        Init Agent instance with Jobs domain instance

        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        raise NotImplementedError
