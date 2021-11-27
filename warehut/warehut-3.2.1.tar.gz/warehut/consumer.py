from multiprocessing import Queue, Value
from queue import Empty as QueueIsEmpty

from typing import Callable
from inspect import iscoroutinefunction

from .worker import Worker
from .packet import Packet



def listen(event):
    """Define function as an event listener"""
    
    def wrapper(f):
        if not iscoroutinefunction(f):
            raise TypeError('Event listeners must be asynchronous')
            
        f.event = event
        return f
        
    return wrapper



class Consumer(Worker):
    """Generic consumer class"""

    listeners: dict[str, Callable]
    queue: Queue
    exceeded_size: int = 65536


    def __init_subclass__(cls):
        # Locate all listener methods
        cls.listeners = {
            obj.event: obj for name, obj in cls.__dict__.items()
            if hasattr(obj, 'event')
        }

    def __init__(self):
        Worker.__init__(self)
        self.queue = Queue(self.exceeded_size)


    async def _mainloop(self):
        while self.status.value:
            try:
                # Await packet and get the assigned listener
                packet = self.queue.get_nowait()
                listener = self.listeners[packet.event]

            except (QueueIsEmpty, KeyError):
                continue

            # Call listener with packet data
            await listener(self, packet.data)
