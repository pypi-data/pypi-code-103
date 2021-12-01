from typing import Dict, List
from breath_api_interface import Request, Response, Queue
from breath_main.session_manager.request_manager.request_handler import RequestHandler


class ResponseHandler(RequestHandler):

    def __init__(self, global_response_queue:Queue):
        super().__init__()

        self._response_queues : Dict[str, Queue] = {}
        self._global_response_queue = global_response_queue

    def register_service(self, service_name:str, response_queue:Queue) -> None:
        self._response_queues[service_name] = response_queue

    def handle(self, request: Request) -> None:
        self._send_for_next(request)
    
    def process_responses(self):
        if not self._global_response_queue.empty():
            response : Response = self._global_response_queue.get()

            service_name = response.requester_service_name
            self._response_queues[service_name].insert(response)