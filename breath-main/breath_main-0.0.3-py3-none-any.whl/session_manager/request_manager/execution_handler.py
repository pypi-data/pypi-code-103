from breath_api_interface.queue import Queue
from breath_api_interface.request import Request
from breath_main.session_manager.request_manager.request_handler import RequestHandler


class ExecutionHandler(RequestHandler):

    def __init__(self):
        super().__init__()

        self._service_registry : dict[str, Queue] = {}

    def register_service(self, service_name:str, service_queue:Queue) -> None:
        '''Register some service

            :param service_name: Name of service being registered.
            :type service_name: str

            :param service_queue: Queue to submit requests for the service 
            :type service_queue: breath_api_interface.Queue
        '''

        self._service_registry[service_name] = service_queue

    def handle(self, request:Request) -> None:
        '''Execute the request.

            :param request: Request to execute.
            :type request: breath_api_interface.Request
        '''

        self._send(request)
        self._send_for_next(request)
    
    def _send(self, request: Request) -> None:
        '''Send the request to the service.

            :param request: Request to execute.
            :type request: breath_api_interface.Request
        '''
        self._service_registry[request.service_name].insert(request)
