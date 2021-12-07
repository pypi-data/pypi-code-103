from .utilities import *


class Event(ABC):
    pass


class EventHandler(ABC):
    # @match_typing
    @abstractmethod
    def handle_event(self, event_to_handle: Event):
        raise NotImplementedError
