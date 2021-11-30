from typing import Callable

from . import StreamConnection
from ...core.session.null_session import NullSession
from ...core.session.stream_service_discovery.null_stream_connection_configuration import (
    NullStreamConnectionConfiguration,
)
from ...tools import cached_property


class NullStreamConnection(StreamConnection):
    def __init__(self):
        StreamConnection.__init__(
            self,
            stream_id=-1,
            name="",
            session=NullSession(),
            config=NullStreamConnectionConfiguration(),
            subprotocol="",
            max_reconnect=0,
        )

    @cached_property
    def subprotocol(self):
        return ""

    @property
    def can_run(self):
        return False

    @property
    def is_ready(self):
        return False

    @property
    def is_disposed(self):
        return False

    @property
    def can_be_disconnect(self):
        return False

    def connect(self):
        # do nothing
        pass

    def disconnect(self):
        # do nothing
        pass

    async def disconnect_async(self):
        # do nothing
        pass

    def dispose(self):
        # do nothing
        pass

    async def dispose_async(self):
        # do nothing
        pass

    def send(self, data: dict) -> None:
        # do nothing
        pass

    def on(self, event: str, listener: Callable) -> None:
        # do nothing
        pass

    def remove_listener(self, event: str, listener: Callable) -> None:
        # do nothing
        pass
