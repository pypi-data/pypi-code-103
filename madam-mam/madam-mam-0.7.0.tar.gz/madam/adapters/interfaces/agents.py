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

import adhesive

from madam.domains.interfaces.agents import AgentInterface, ApplicationAgentInterface


class AdhesiveAgentInterface(AgentInterface):
    """
    AdhesiveAgentInterface adapter class
    """

    @abc.abstractmethod
    def execute(self, context: adhesive.ExecutionToken):
        """
        Execute agent code

        :param context: adhesive.ExecutionToken instance
        :return:
        """
        raise NotImplementedError


class AdhesiveApplicationAgentInterface(ApplicationAgentInterface):
    """
    AdhesiveApplicationAgentInterface adapter class
    """

    @abc.abstractmethod
    def execute(self, context: adhesive.ExecutionToken):
        """
        Execute agent code

        :param context: adhesive.ExecutionToken instance
        :return:
        """
        raise NotImplementedError
