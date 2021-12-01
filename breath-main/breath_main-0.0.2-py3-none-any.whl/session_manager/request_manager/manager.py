from breath_api_interface import ProcessQueue, Queue, service_interface
from breath_main.session_manager.request_manager.availability_handler import AvailabilityHandler
from breath_main.session_manager.request_manager.execution_handler import ExecutionHandler
from breath_main.session_manager.request_manager.incoming_handler import IncomingHandler
from breath_main.session_manager.request_manager.permission_handler import PermissionHandler
from breath_main.session_manager.request_manager.response_handler import ResponseHandler
from breath_main.session_manager.request_manager.validation_handler import ValidationHandler


class RequestManager:
    '''Manages the processing of a request.

        :ivar incoming_queue: Queue for incoming requests
        :type incoming_queue: breath_api_interface.Queue
        :ivar _incoming_queue: Queue for incoming requests
        :type _incoming_queue: breath_api_interface.Queue
    '''

    def __init__(self, incoming_queue:Queue, global_response_queue:Queue, session_manager):
        '''RequestManager constructor.

            Initializes the processing pipeline.    
        '''
        self._incoming_queue : Queue = incoming_queue
        self._session_manager  = session_manager
        self._global_request_queue = global_response_queue
        self._start_pipeline()

    def _start_pipeline(self) -> None:
        '''Initializes the processing pipeline.    
        '''
        self._incoming_handler = IncomingHandler(self._incoming_queue)
        self._validation_handler = ValidationHandler()
        self._availability_handler = AvailabilityHandler(self._session_manager)
        self._permission_handler = PermissionHandler()
        self._execution_handler = ExecutionHandler()
        self._response_handler = ResponseHandler(self._global_request_queue)

        self._incoming_handler.next = self._validation_handler
        self._validation_handler.next = self._availability_handler
        self._availability_handler.next = self._permission_handler
        self._permission_handler.next = self._execution_handler
        self._execution_handler.next = self._response_handler
    
    def register_service(self, service_name:str, request_queue:Queue, response_queue:Queue,  permission_info:dict = {}) -> None:
        '''Register a new service.
        '''
        self._availability_handler.register_service(service_name)
        self._execution_handler.register_service(service_name, request_queue)
        self._permission_handler.register_service(service_name, permission_info)
        self._response_handler.register_service(service_name, response_queue)
    
    def process_request(self):
        self._incoming_handler.process_request()
        self._response_handler.process_responses()

    def change_user_level(self, user_level):
        self._permission_handler.user_level = user_level