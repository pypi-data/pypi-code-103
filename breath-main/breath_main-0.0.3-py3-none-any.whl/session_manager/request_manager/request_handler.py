from __future__ import annotations
from abc import ABC, abstractmethod

from breath_api_interface import SimpleQueue, Request


#Import annotations for class type hint inside itself in versions <3.10.x
import sys

class RequestHandler(ABC): 
    def __init__(self):
        self._next = None 
    
    @property
    def next(self) -> RequestHandler:
        return self._next
    
    @next.setter
    def next(self, value:RequestHandler) -> None:
        self._next = value

    def _send_for_next(self, request:Request) -> None:
        if self._next is not None:
            self._next.handle(request)

    @abstractmethod
    def handle(self, request:Request) -> None:
        ...