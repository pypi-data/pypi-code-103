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
from typing import Optional

import adhesive
from adhesive import (
    AdhesiveProcess,
    ConsoleUserTaskProvider,
    ProcessExecutor,
    UserTaskProvider,
    config,
    configure_logging,
)
from adhesive.process_read.bpmn import read_bpmn_content

from madam.adapters import agents
from madam.adapters.interfaces.agents import (
    AdhesiveAgentInterface,
    AdhesiveApplicationAgentInterface,
)
from madam.domains.applications import Applications
from madam.domains.interfaces.agents import ApplicationAgentInterface
from madam.domains.interfaces.bpmn import BPMNEngineInterface, BPMNXMLParserInterface
from madam.domains.jobs import Jobs


class AdhesiveBPMNEngine(BPMNEngineInterface):
    # pylint: disable=super-init-not-called
    # bug reported, see https://github.com/PyCQA/pylint/issues/4790
    def __init__(
        self,
        content: str,
        bpmn_parser: BPMNXMLParserInterface,
        jobs: Jobs,
        applications: Applications,
    ):
        __doc__ = (  # pylint: disable=redefined-builtin, disable=unused-variable
            BPMNEngineInterface.__init__.__doc__
        )
        self.content = content
        self.bpmn_parser = bpmn_parser
        self.jobs = jobs
        self.applications = applications
        self.process = self.get_process_executor_from_content(content)
        self.define_service_tasks()

    def define_service_tasks(self):
        """
        Create AdhesiveAgent instances from content service types
        Create adhesive tasks with AdhesiveAgent.execute method
        Add adhesive task in adhesive process

        :return:
        """
        # import agents from workflow services in BPMN XML
        for service_type in self.bpmn_parser.get_service_types(self.content):
            module_reference_path = f"{agents.__package__}.{service_type}"
            module = importlib.import_module(module_reference_path)
            # get agent class from module
            agent_class = None
            for module_attribute_name in dir(module):
                module_attribute = getattr(module, module_attribute_name)
                if inspect.isclass(module_attribute):
                    module_attribute_parents = inspect.getmro(module_attribute)
                    if len(module_attribute_parents) > 1 and (
                        module_attribute_parents[1] == AdhesiveApplicationAgentInterface
                        or module_attribute_parents[1] == AdhesiveAgentInterface
                    ):
                        agent_class = module_attribute
                        break
            if agent_class is None:
                raise LookupError(f"No agent class in agent module {module.__name__}")
            if ApplicationAgentInterface in inspect.getmro(agent_class):
                agent_instance = agent_class(self.jobs, self.applications)
            else:
                agent_instance = agent_class(self.jobs)

            task_type_already_in_task_definitions = False
            for task in self.process.adhesive_process.task_definitions:
                if task.expressions == (agent_class.AGENT_TYPE,):
                    task_type_already_in_task_definitions = True

            task_type_already_in_chained_task_definitions = False
            for task in self.process.adhesive_process.chained_task_definitions:
                if task.expressions == (agent_class.AGENT_TYPE,):
                    task_type_already_in_chained_task_definitions = True

            if (
                task_type_already_in_task_definitions is False
                or task_type_already_in_chained_task_definitions is False
            ):
                # replace adhesive decorator
                adhesive_task = adhesive.ExecutionTask(
                    code=agent_instance.execute,
                    expressions=(agent_class.AGENT_TYPE,),
                    regex_expressions=None,
                    loop=None,
                    when=None,
                    lane=None,
                    deduplicate=None,
                )
                if task_type_already_in_task_definitions is False:
                    self.process.adhesive_process.task_definitions.append(adhesive_task)
                if task_type_already_in_chained_task_definitions is False:
                    self.process.adhesive_process.chained_task_definitions.append(
                        adhesive_task
                    )

    def start(self, variables: dict) -> dict:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            BPMNEngineInterface.start.__doc__
        )
        execution_data = self.process.execute(initial_data=variables)

        return execution_data.as_dict()

    def stop(self):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            BPMNEngineInterface.stop.__doc__
        )
        # there is no way to stop threads (futures)

    @staticmethod
    def get_process_executor_from_content(
        content: str,
        ut_provider: Optional[UserTaskProvider] = None,
        wait_tasks: bool = True,
    ):
        """
        Get process executor instance

        :param content: BPMN XML content
        :param ut_provider: UserTaskProvider instance (default=None)
        :param wait_tasks: True to wait tasks (default=True)
        :return:
        """
        process = AdhesiveProcess("_root")

        process.process = read_bpmn_content(content)
        configure_logging(config.current)

        if ut_provider is None:
            ut_provider = ConsoleUserTaskProvider()

        return ProcessExecutor(process, ut_provider=ut_provider, wait_tasks=wait_tasks)
