class StreamStateEvent:
    OPENING = "opening_state_event"
    OPENED = "opened_state_event"
    CLOSING = "closing_state_event"
    CLOSED = "closed_state_event"
    PAUSING = "pausing_state_event"
    PAUSED = "paused_state_event"


class StreamEvent:
    # broadcast events
    UPDATE = "update_stream_event"
    REFRESH = "refresh_stream_event"
    STATUS = "status_stream_event"
    COMPLETE = "complete_stream_event"
    ERROR = "error_stream_event"
    ACK = "ack_stream_event"
    RESPONSE = "response_stream_event"
    ALARM = "alarm_stream_event"

    # specific events
    _UPDATE = "update_stream_{}_event"
    _REFRESH = "refresh_stream_{}_event"
    _STATUS = "status_stream_{}_event"
    _COMPLETE = "complete_stream_{}_event"
    _ERROR = "error_stream_{}_event"
    _ACK = "ack_stream_{}_event"
    _RESPONSE = "response_stream_{}_event"
    _ALARM = "alarm_stream_{}_event"

    def __init__(self, stream_id) -> None:
        self.update = self._UPDATE.format(stream_id)
        self.refresh = self._REFRESH.format(stream_id)
        self.status = self._STATUS.format(stream_id)
        self.complete = self._COMPLETE.format(stream_id)
        self.error = self._ERROR.format(stream_id)
        self.ack = self._ACK.format(stream_id)
        self.response = self._RESPONSE.format(stream_id)
        self.alarm = self._ALARM.format(stream_id)


class StreamCxnEvent(object):
    # broadcast events
    CONNECTING = "connecting_cxn_event"
    CONNECTED = "connected_cxn_event"
    READY = "ready_cxn_event"
    DISCONNECTING = "disconnecting_cxn_event"
    DISCONNECTED = "disconnected_cxn_event"
    DISPOSED = "disposed_cxn_event"
    RECONNECTING = "reconnecting_cxn_event"


class StreamEventPool(object):
    _pool = {}

    @classmethod
    def pop(cls, stream_id: int) -> "StreamEvent":
        event = cls._pool.pop(stream_id, StreamEvent(stream_id))
        return event

    @classmethod
    def push(cls, event: "StreamEvent", stream_id) -> None:
        cls._pool[stream_id] = event
