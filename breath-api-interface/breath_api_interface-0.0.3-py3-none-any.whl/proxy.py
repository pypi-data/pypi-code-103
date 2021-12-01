import time
from typing import Union

from .request import Request, Response

from .queue import Queue

class ServiceProxy:
    '''Provides acess for BReATH services.

        :ivar manager_queue: Queue for send requests
        :type manager_queue: breath.api_interface.Queue

        :ivar response_queue: Queue for getting requests responses
        :type response_queue: breath.api_interface.Queue
    '''

    def __init__(self, manager_queue:Queue, response_queue:Queue):
        '''ServiceProxy constructor.

            :param manager_queue: Queue for send requests
            :type manager_queue: breath.api_interface.Queue

            :param response_queue: Queue for getting requests responses
            :type response_queue: breath.api_interface.Queue
        '''
        self.manager_queue = manager_queue
        self.response_queue = response_queue

    def send_request(self, request: Request) -> Union[Response, None]:
        '''
            Send some service request.

            Blocks the code while waiting for response. It might be better to use multithreading.
        
            :param request: Request to be send.
            :type request: breath.api_interface.Request

            :return: Request response or None if request "wait_for_response" is false.
            :rtype: Response|None
        '''        
        while self.manager_queue.full():
            continue
        
        self.manager_queue.insert(request)

        if not request.wait_for_response:
            return None

        while self.response_queue.empty():
            time.sleep(1E-3)

        response = self.response_queue.get()

        return response