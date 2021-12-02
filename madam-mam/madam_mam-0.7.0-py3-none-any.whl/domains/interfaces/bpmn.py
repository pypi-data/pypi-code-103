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
from typing import List, NamedTuple, Optional

from madam.domains.applications import Applications
from madam.domains.jobs import Jobs


class BPMNData(NamedTuple):
    """
    BPMNData namedtuple class
    """

    id: str
    name: str
    timer: Optional[str]


class BPMNXMLParserInterface(abc.ABC):
    """
    BPMNXMLParserInterface class
    """

    @abc.abstractmethod
    def get_workflow_data(self, content: str) -> BPMNData:
        """
        Parse BPMN data from xml

        Return a namedtuple with id, name and timer fields

        :param content: XML content
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_service_types(self, content: str) -> List[str]:
        """
        Return list of required services in workflow content

        :param content: BPMN XML string
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def validate_xml_schema(self, content: str) -> None:
        """
        Validate xml schema against BPMN XSD

        :param content: XML content
        :return:
        """
        raise NotImplementedError


class BPMNEngineInterface(abc.ABC):
    """
    BPMNEngineInterface class
    """

    @abc.abstractmethod
    def __init__(
        self,
        content: str,
        bpmn_parser: BPMNXMLParserInterface,
        jobs: Jobs,
        applications: Applications,
    ):
        """
        Init BPMNEngine with BPMN XML content

        :param content: BPMN XML content
        :param bpmn_parser: BPMNXMLParser domain instance
        :param jobs: Jobs domain instance
        :param applications: Applications domain instance
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start(self, variables: dict) -> dict:
        """
        Start BPMN engine with initial variables

        Return the final variables of the workflow instance

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        """
        Stop BPMN engine

        :return:
        """
        raise NotImplementedError
