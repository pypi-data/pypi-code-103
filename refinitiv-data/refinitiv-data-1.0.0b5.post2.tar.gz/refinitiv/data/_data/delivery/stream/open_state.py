from enum import auto, Enum

from .stream_state import StreamState


class OpenState(Enum):
    Opened = auto()
    Pending = auto()
    Closed = auto()


stream_state_to_open_state = {
    StreamState.Opened: OpenState.Opened,
    StreamState.Opening: OpenState.Opened,
    StreamState.Paused: OpenState.Pending,
    StreamState.Pausing: OpenState.Pending,
    StreamState.Closed: OpenState.Closed,
    StreamState.Closing: OpenState.Closed,
}
