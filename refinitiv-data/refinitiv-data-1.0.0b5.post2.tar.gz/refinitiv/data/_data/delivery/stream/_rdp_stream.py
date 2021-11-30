# coding: utf-8

from typing import TYPE_CHECKING, Callable, Any

from ._protocol_type import ProtocolType
from ._stream_listener import RDPStreamListener
from .stream import Stream, update_message_with_extended_params
from ...content._content_type import ContentType
from ...tools import cached_property

if TYPE_CHECKING:
    from . import StreamConnection
    from ...content._types import ExtendedParams
    from ...core.session import Session


class _RDPStream(Stream, RDPStreamListener["_RDPStream"]):
    def __init__(
        self,
        stream_id: int,
        content_type: ContentType,
        session: "Session",
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        extended_params: "ExtendedParams" = None,
        on_ack: Callable = None,
        on_response: Callable = None,
        on_update: Callable = None,
        on_alarm: Callable = None,
    ):
        Stream.__init__(self, stream_id, content_type, session)
        RDPStreamListener.__init__(
            self,
            loop=session.loop,
            logger=session.logger(),
            on_ack=on_ack,
            on_response=on_response,
            on_update=on_update,
            on_alarm=on_alarm,
        )

        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters
        self._extended_params = extended_params

    @property
    def service(self) -> str:
        return self._service

    @property
    def universe(self) -> list:
        return self._universe

    @property
    def view(self) -> list:
        return self._view

    @property
    def parameters(self) -> dict:
        return self._parameters

    @property
    def extended_params(self) -> "ExtendedParams":
        return self._extended_params

    @property
    def name(self) -> str:
        return str(self._universe)

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.RDP

    @cached_property
    def close_message(self):
        close_message = {"streamID": f"{self.id:d}", "method": "Close"}
        return close_message

    @cached_property
    def open_message(self) -> dict:
        message = {
            "streamID": f"{self.id:d}",
            "method": "Subscribe",
            "universe": self.universe,
        }

        if self.service is not None:
            message["service"] = self.service

        if self.view is not None:
            message["view"] = self.view

        if self.parameters is not None:
            message["parameters"] = self.parameters

        if self.extended_params:
            message = update_message_with_extended_params(message, self.extended_params)

        return message

    async def _do_open_async(self, *args, **kwargs) -> None:
        await self._initialize_cxn_async()

        self._cxn.on(self._event.ack, self._on_stream_ack)
        self._cxn.on(self._event.update, self._on_stream_update)
        self._cxn.on(self._event.response, self._on_stream_response)
        self._cxn.on(self._event.alarm, self._on_stream_alarm)

        await super()._do_open_async(*args, **kwargs)

    def _dispose(self):
        self._debug(f"{self._classname} disposing [d]")
        self._cxn.remove_listener(self._event.ack, self._on_stream_ack)
        self._cxn.remove_listener(self._event.update, self._on_stream_update)
        self._cxn.remove_listener(self._event.response, self._on_stream_response)
        self._cxn.remove_listener(self._event.alarm, self._on_stream_alarm)

        self._release_cxn()

        self._debug(f"{self._classname} disposed [D]")

    def _do_on_stream_response(self, originator: "StreamConnection", *args) -> Any:
        if self.is_opening:
            self._loop.call_soon_threadsafe(self._opened.set_result, True)

        else:
            raise ValueError(
                f"{self._classname} Don't know what to do, state={self.state}"
            )

        return args

    def _do_on_stream_ack(self, originator: "StreamConnection", *args) -> Any:
        message = args[0]
        message_state = message.get("state", {})
        stream_state = message_state.get("stream")

        if stream_state == "Closed":
            self._debug(
                f"{self._classname} received a closing message, "
                f"message_state={message_state}, state={self.state}"
            )

            if self.is_opening:
                self._loop.call_soon_threadsafe(self._opened.set_result, False)

            elif self.is_closing:
                self._loop.call_soon_threadsafe(self._closed.set_result, True)

            else:
                raise ValueError(
                    f"{self._classname} Don't know what to do, state={self.state}"
                )

        return args

    def _do_on_stream_alarm(self, originator, *args) -> Any:
        """
        {
            "data": [],
            "state": {
                "id": "QPSValuation.ERROR_REQUEST_TIMEOUT",
                "code": 408,
                "status": "ERROR",
                "message": "The request could not be executed
                            within the service allocated time",
                "stream": "Open"
            },
            "type": "Alarm",
            "streamID": "3"
        }
        """
        message = args[0]
        message_state = message.get("state", {})
        message_state_id = message_state.get("id", "")

        if message_state_id == "QPSValuation.ERROR_REQUEST_TIMEOUT":
            self._error(f"{message}")

            if self.is_opening:
                self._loop.call_soon_threadsafe(self._opened.set_result, False)

            else:
                raise ValueError(
                    f"{self._classname} Don't know what to do, state={self.state}"
                )

        return args
