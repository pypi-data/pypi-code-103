from typing import Dict
from .queue import ProcessQueue, Queue


class Response:
    def __init__(self, sucess:bool, requester_service_name:str, response_data:dict=None, wait_for_response=True):
        self.sucess = sucess
        self.response_data = response_data
        self.requester_service_name = requester_service_name
        self.wait_for_response = wait_for_response

class Request:
    '''Stores some request info.
    '''

    def __init__(self, service_name:str, operation_name:str, response_service_name:str, request_info:dict=None, wait_for_response:bool=True):
        '''Request constructor

            :param service_name: Name of requested service
            :type service_name: str

            :param operation_name: Name of requested operation
            :type operation_name: str

            :param response_service_name: Service that requested the operation
            :type response_service_name: str

            :param request_info: Request parameters
            :type request_info: dict
            
            :param wait_for_response: If the proxy should wait and the requested service should send the response.
            :type wait_for_response: bool
        '''
        
        self.service_name = service_name
        self.operation_name = operation_name
        self.request_info = request_info
        self.response_service_name = response_service_name
        self.wait_for_response = wait_for_response

    def create_response(self, sucess:bool, response_data:dict=None) -> Response:
        return Response(sucess, self.response_service_name, response_data, self.wait_for_response)
