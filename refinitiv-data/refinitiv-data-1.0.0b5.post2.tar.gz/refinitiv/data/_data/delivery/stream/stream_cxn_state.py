from enum import Enum, unique, auto


@unique
class StreamCxnState(Enum):
    Initial = auto()
    Connecting = auto()
    Connected = auto()
    Ready = auto()
    Disconnecting = auto()
    Disconnected = auto()
    Reconnecting = auto()
    Disposed = auto()
