from abc import ABC, abstractmethod
from typing import Union
from breath_api_interface import request

from breath_api_interface.request import Response
from breath_data.data_workflow import DataWorkflow

class Workflow(ABC):

    def __init__(self, workflow_service:DataWorkflow, workflow_name:str):
        self.__service = workflow_service
        self._workflow_name = workflow_name

    def _send_bdap_request(self, operation_name, request_info=None, wait_for_response=False) -> Union[Response, None]:
        return self.__service._send_request("BDAcessPoint", operation_name, request_info, wait_for_response)

    def run(self, force_run = False):

        if not force_run:
            response = self._send_bdap_request("is_workflow_runned", {"workflow_name":self._workflow_name})

            if response.sucess == True:
                return

        self._workflow_run()

    @abstractmethod
    def _workflow_run(self):
        ...