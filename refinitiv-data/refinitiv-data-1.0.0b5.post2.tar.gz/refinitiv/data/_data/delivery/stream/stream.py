# coding: utf8
import asyncio
from typing import Optional, Any
from typing import TYPE_CHECKING

from ._protocol_type import ProtocolType
from ._stream_cxn_cache import stream_cxn_cache
from .event import StreamEvent, StreamEventPool, StreamCxnEvent
from .stream_state import StreamState
from .stream_state_manager import StreamStateManager
from ...core.session.tools import is_closed

if TYPE_CHECKING:
    from ...content import ContentType
    from ..stream import StreamConnection
    from ...core.session import Session


class Stream(StreamStateManager):
    _cxn: Optional["StreamConnection"] = None
    _event: Optional[StreamEvent] = None
    _with_updates: bool = True
    _closed: Optional[asyncio.Future] = None
    _opened: Optional[asyncio.Future] = None

    def __init__(
        self,
        stream_id: int,
        content_type: "ContentType",
        session: "Session",
    ) -> None:
        StreamStateManager.__init__(self, loop=session.loop, logger=session.logger())
        self._id: int = stream_id
        self._content_type: "ContentType" = content_type
        self._session: "Session" = session
        self._loop: "asyncio.AbstractEventLoop" = session.loop
        self._classname = f"[{self.__class__.__name__} id={self.id}]"

    @property
    def classname(self):
        return self._classname

    @property
    def id(self) -> int:
        return self._id

    @property
    def session(self) -> "Session":
        return self._session

    @property
    def name(self) -> str:
        return ""

    @property
    def content_type(self) -> "ContentType":
        return self._content_type

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.NONE

    @property
    def close_message(self) -> dict:
        return {}

    @property
    def open_message(self) -> dict:
        return {}

    async def open_async(self, *args, with_updates: bool = True) -> StreamState:
        if is_closed(self._session):
            raise AssertionError("Session must be open")

        return await super().open_async(with_updates=with_updates)

    def send(self, message) -> None:
        self._debug(f"{self._classname} send message={message}")
        self._cxn.send(message)

    async def _initialize_cxn_async(self):
        self._event = StreamEventPool.pop(self.id)
        self._cxn = await stream_cxn_cache.get_cxn_async(
            self.session, self.content_type, self.protocol_type
        )
        self._cxn.on(StreamCxnEvent.DISCONNECTING, self.close)
        self._cxn.on(StreamCxnEvent.DISPOSED, self.halt)

    def _release_cxn(self):
        self._cxn.remove_listener(StreamCxnEvent.DISCONNECTING, self.close)
        self._cxn.remove_listener(StreamCxnEvent.DISPOSED, self.halt)
        self._debug(f"{self._classname} release cxn={self._cxn}")
        stream_cxn_cache.release(self.session, self.content_type)
        self._cxn = None
        StreamEventPool.push(self._event, self.id)

    async def _do_open_async(self, *args, **kwargs) -> None:
        self._opened = self._loop.create_future()
        self.send(self.open_message)

        await self._opened

    async def _do_close_async(self, *args, **kwargs):
        self._closed = self._loop.create_future()
        self.send(self.close_message)
        self._dispose()

    def _do_on_stream_error(self, originator, *args) -> Any:
        if self.is_opening:
            self._loop.call_soon_threadsafe(self._opened.set_result, False)

        return args


def update_message_with_extended_params(message: dict, extended_params: dict) -> dict:
    return update_key_in_dict(message, extended_params)


def update_key_in_dict(message: dict, extended_params: dict) -> dict:
    for param, extended_val in extended_params.items():
        if param in message:
            prev_value = message[param]
            if isinstance(prev_value, dict) and isinstance(extended_val, dict):
                update_key_in_dict(prev_value, extended_val)
            else:
                message[param] = extended_val
        else:
            message[param] = extended_val

    return message
