from abc import ABC, abstractmethod
from typing import Union

from breath_api_interface import ServiceProxy, Queue, Request
from breath_api_interface.request import Response


class Service(ABC):
    '''BReATH service base class.
    '''

    def __init__(self, proxy:ServiceProxy, request_queue:Queue, global_response_queue:Queue, service_name:str):
        '''Service constructor.

            :param proxy: Proxy for sending requests
            :type proxy: breath_api_interface.ServiceProxy

            :param request_queue: Queue for getting requests
            :type request_queue: Queue
        '''
        self.__proxy = proxy
        self._request_queue = request_queue
        self._global_response_queue = global_response_queue
        self._service_name = service_name

    @property
    def request_queue(self) -> Queue:
        '''Get the queue for sending requests.
        '''
        return self._request_queue

    def _get_request(self) -> Union[Request, None]:
        '''Get some request, if available
        '''
        if not self._request_queue.empty():
            return self._request_queue.pop()
        else:
            return None

    def _send_request(self, service_name, operation_name, request_info=None, wait_for_response=True) -> Union[Response, None]:
        request = Request(service_name, operation_name, self._service_name, request_info, wait_for_response)
        return self.__proxy.send_request(request)

    def _send_response(self, response:Response) -> None:
        if response.wait_for_response == True:
            self._global_response_queue.insert(response)
    
    def run_forever(self):
        while(True):
            self.run()

    @abstractmethod
    def run(self):
        '''Run the service.
        '''
        ...