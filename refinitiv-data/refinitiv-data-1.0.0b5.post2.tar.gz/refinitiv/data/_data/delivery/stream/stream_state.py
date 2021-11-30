from enum import Enum, unique, auto


@unique
class StreamState(Enum):
    Opening = auto()
    Opened = auto()
    Closing = auto()
    Closed = auto()
    Pausing = auto()
    Paused = auto()
