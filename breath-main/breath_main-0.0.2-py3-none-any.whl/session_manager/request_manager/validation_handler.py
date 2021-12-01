from breath_api_interface.request import Request
from breath_main.session_manager.request_manager.request_handler import RequestHandler


class ValidationHandler(RequestHandler):
    def __init__(self):
        '''ValidationHandler Constructor.
        '''

        super().__init__()

    def handle(self, request:Request) -> None:
        '''Validates the request, looking for inconsistencies.

            TODO Implementar validação
        '''
        self._send_for_next(request)