from breath_api_interface.queue import ProcessQueue, Queue
from breath_api_interface.request import Request
from breath_main.session_manager.request_manager.request_handler import RequestHandler


class IncomingHandler(RequestHandler):

    def __init__(self, incoming_queue:Queue):
        super().__init__()
        self._incoming_queue = incoming_queue

    def process_request(self):
        if not self._incoming_queue.empty():
            self.handle(self._incoming_queue.pop())

    def handle(self, request:Request) -> None:
        self._send_for_next(request)