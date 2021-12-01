from multiprocessing import Value
import time


from breath_api_interface.service_interface import Service
from breath_api_interface.proxy import ServiceProxy
from breath_api_interface.queue import ProcessQueue
from breath_api_interface.request import Request

from breath_main.session_manager.request_manager.manager import RequestManager
from breath_main.session_manager.service_constructor import ProcessServiceConstructor



class ProcessSessionManager:
    def __init__(self):
        self._queue = ProcessQueue()
        self._global_response_queue = ProcessQueue()
        self._sm_response_queue = ProcessQueue()

        self._service_constructor = ProcessServiceConstructor()
        self._request_manager = RequestManager(self._queue, self._global_response_queue, self)

        self._request_manager.register_service("SESSION_MANAGER", None, self._sm_response_queue)

    def create_service(self, service_name:str):
        request_queue, response_queue = self._service_constructor.create_service(service_name, self._queue, self._global_response_queue)

        if request_queue is None:
            raise ValueError("Service "+service_name+" is invalid")

        self._request_manager.register_service(service_name, request_queue, response_queue)

    def run(self):
        self._request_manager.process_request()

    def send_request(self, service_name, operation_name, request_info=None, wait_for_response=True):
        request = Request(service_name, operation_name, "SESSION_MANAGER", request_info, wait_for_response)
        
        self._queue.insert(request)

        if not wait_for_response:
            return True
        
        while self._sm_response_queue.empty():
            self.run()
            time.sleep(1E-3)

        

        return self._sm_response_queue.get()

    def __del__(self):
        del self._service_constructor