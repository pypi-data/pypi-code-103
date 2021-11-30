from breath_api_interface.proxy import ServiceProxy
from breath_api_interface.queue import ProcessQueue
from breath_api_interface.request import Request
from breath_main.session_manager.request_manager.manager import RequestManager
from breath_main.session_manager.service_constructor import ProcessServiceConstructor


from breath_api_interface.service_interface import Service

class ProcessSessionManager:
    def __init__(self):
        self._queue = ProcessQueue()
        self._global_response_queue = ProcessQueue()

        self._service_constructor = ProcessServiceConstructor()
        self._request_manager = RequestManager(self._queue, self._global_response_queue, self)

    def create_service(self, service_name:str) -> bool:
        request_queue, response_queue = self._service_constructor.create_service(service_name, self._queue, self._global_response_queue)

        if request_queue is None:
            return False

        self._request_manager.register_service(service_name, request_queue, response_queue)

        return True

    def run(self):
        self._request_manager.process_request()