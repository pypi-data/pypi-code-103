from .utilities import *
from .concepts import EventHandler, Event
from .elements import EventListener


class EventBus(EventHandler):
    def __init__(self):
        self.listeners: Dict[Type, List[EventListener]] = dict()

    # @match_typing
    def add_listener(self, listener: EventListener, type_to_listen: Type) -> None:
        if type_to_listen not in self.listeners:
            self.listeners[type_to_listen] = [listener]
        else:
            self.listeners[type_to_listen].append(listener)

    # @match_typing
    def handle_event(self, event_to_handle: Event):
        event_type: Type = type(event_to_handle)
        for listed_type in self.listeners:
            if issubclass(event_type, listed_type):
                for event_listener in self.listeners[listed_type]:
                    event_listener.process_event(event_to_handle)
