import time
from queue import Queue

from .utilities import *
from .concepts import Event, EventHandler


class InternalPipelineElement(ABC):
    def __init__(self):
        pass


class EventListener(InternalPipelineElement, ABC):
    def __init__(self):
        super().__init__()

    # @match_typing
    @abstractmethod
    def process_event(self, event: Event) -> None:
        raise NotImplementedError


class EventGenerator(InternalPipelineElement, ABC):
    def __init__(self):
        super().__init__()
        self.event_handler: Optional[EventHandler] = None

    def process_generated_event(self, event: Event) -> None:
        if self.event_handler is None:
            raise Exception  # TODO
        else:
            self.event_handler.handle_event(event)


class EventSource(EventGenerator, ABC):
    pass


class TriggererEventSource(EventSource, ABC):
    @abstractmethod
    def start_generating(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_generating(self) -> None:
        raise NotImplementedError


class TriggerableEventSource(EventSource, ABC):
    @abstractmethod
    def get_event(self) -> Event:
        raise NotImplementedError

    def generate_event(self) -> None:
        self.event_handler.handle_event(self.get_event())


class TriggerableEventBatchSource(TriggerableEventSource, ABC):
    def __init__(self):
        super().__init__()
        self.queue: Queue = Queue()

    @abstractmethod
    def get_event_batch(self) -> List[Event]:
        raise NotImplementedError

    def get_event(self) -> None:
        while self.queue.empty():
            [self.queue.put(x) for x in self.get_event_batch()]
            if self.queue.empty():
                time.sleep(1)
        return self.queue.get(block=False)


class EventSink(EventListener):
    # @match_typing
    @abstractmethod
    def drown_event(self, event: Event) -> None:
        raise NotImplementedError

    # @match_typing
    def process_event(self, event: Event) -> None:
        self.drown_event(event)


class EventAnalyzer(EventGenerator, EventListener):
    # @match_typing
    @abstractmethod
    def analyze_event(self, input_event: Event, output_event_handler: EventHandler) -> None:
        raise NotImplementedError

    # @match_typing
    def process_event(self, event: Event) -> None:
        self.analyze_event(event, self.event_handler)
