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

from importlib import util
from io import StringIO
from typing import List
from xml.etree import ElementTree

from lxml import etree

from madam.adapters import agents
from madam.domains.entities.constants import BPMN_XSD_PATH
from madam.domains.interfaces.bpmn import BPMNData, BPMNXMLParserInterface


class ZeebeeBPMNXMLParser(BPMNXMLParserInterface):
    """
    ZeebeeBPMNXMLParser domain class
    """

    @staticmethod
    def get_xml_namespaces(content: str) -> dict:
        """
        Get namespaces from XML content

        :param content: XML content
        :return:
        """
        return {
            node[0]: node[1]
            for _, node in ElementTree.iterparse(StringIO(content), events=["start-ns"])
        }

    def get_workflow_data(self, content: str) -> BPMNData:
        """
        Parse BPMN data from xml

        Return a namedtuple with id, name and timer fields

        :param content: XML content
        :return:
        """
        namespaces = self.get_xml_namespaces(content)
        root = ElementTree.fromstring(content)

        # get id and name from content
        process_node = root.find("bpmn:process", namespaces)
        if process_node is None:
            raise Exception("Invalid BPMN XML, node process not found")
        id_ = process_node.attrib["id"]
        if "name" in process_node.attrib:
            name = process_node.attrib["name"]
        else:
            name = id_

        start_event = process_node.find("bpmn:startEvent", namespaces)
        if start_event is None:
            raise Exception("Invalid BPMN XML, node startEvent not found")

        timer = None
        # detect if cyclic timer exists
        timer_cyclic_node = start_event.find(
            "bpmn:timerEventDefinition/bpmn:timeCycle", namespaces
        )
        if timer_cyclic_node is not None:
            if (
                timer_cyclic_node.attrib[f"{{{namespaces['xsi']}}}type"]
                != "bpmn:tFormalExpression"
            ):
                raise Exception(
                    "Cyclic timer start event expression type not supported"
                )
            timer = timer_cyclic_node.text

        # detect if date timer exists
        timer_date_node = start_event.find(
            "bpmn:timerEventDefinition/bpmn:timeDate", namespaces
        )
        if timer_date_node is not None:
            if (
                timer_date_node.attrib[f"{{{namespaces['xsi']}}}type"]
                != "bpmn:tFormalExpression"
            ):
                raise Exception("Date timer start event expression type not supported")
            timer = timer_date_node.text

        # check that zeebe service type exists in madam agents...
        for service_type in self.get_service_types(content):
            module_reference_path = f"{agents.__package__}.{service_type}"
            find_spec = util.find_spec(module_reference_path)
            if find_spec is None:
                raise Exception(f"Invalid Madam agent not found: {service_type}")

        return BPMNData(id_, name, timer)

    def get_service_types(self, content: str) -> List[str]:
        """
        Return Zeebe service types in workflow

        :param content: BPMN XML string
        :return:
        """
        namespaces = {
            node[0]: node[1]
            for _, node in ElementTree.iterparse(StringIO(content), events=["start-ns"])
        }
        root = ElementTree.fromstring(content)

        # return list of unique types
        return list(
            (
                task_definition.attrib["type"]
                for task_definition in root.findall(
                    ".//bpmn:serviceTask/bpmn:extensionElements/zeebe:taskDefinition[@type]",
                    namespaces,
                )
            )
        )

    def validate_xml_schema(self, content: str) -> None:
        """
        Validate xml schema against BPMN XSD

        :param content: XML content
        :return:
        """
        # Create the schema object
        with open(BPMN_XSD_PATH, encoding="utf-8") as filehandle:
            xmlschema_doc = etree.parse(filehandle)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # Create a tree for the XML document
        doc = etree.fromstring(content.encode("utf-8"))
        # Validate the XML document upon the XSD schema
        xmlschema.assertValid(doc)
