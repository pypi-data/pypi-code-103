# coding: utf-8

from typing import Any, TYPE_CHECKING

import pandas as pd

from ..._content_type import ContentType
from ....core.session import get_valid_session
from ....delivery.stream import _RDPStream, StreamStateEvent
from ....delivery.stream._stream_factory import create_rdp_stream
from ....delivery.stream._stream_listener import RDPStreamListener
from ....tools import cached_property

if TYPE_CHECKING:
    from ....delivery.stream import StreamState


class QuantitativeDataStream(RDPStreamListener["QuantitativeDataStream"]):
    def __init__(
        self,
        universe: dict,
        fields: list = None,
        extended_params: dict = None,
        session: object = None,
    ):
        session = get_valid_session(session)
        RDPStreamListener.__init__(self, loop=session.loop, logger=session.logger())

        self._session = session
        self._universe = universe
        self._fields = fields
        self._extended_params = extended_params

        if extended_params and "view" in extended_params:
            self._column_names = extended_params["view"]

        else:
            self._column_names = fields or None

        self._data = None
        self._headers = None

    @property
    def state(self):
        return self._stream.state

    @property
    def universe(self):
        return self._universe

    @cached_property
    def _stream(self) -> _RDPStream:
        stream = create_rdp_stream(
            ContentType.STREAMING_CONTRACTS,
            session=self._session,
            service=None,
            view=self._fields,
            parameters=None,
            universe=self._universe,
            extended_params=self._extended_params,
        )
        stream.on(StreamStateEvent.CLOSED, lambda *_: self.close())
        stream.on_ack(self._on_stream_ack)
        stream.on_response(self._on_stream_response)
        stream.on_update(self._on_stream_update)
        stream.on_alarm(self._on_stream_alarm)
        return stream

    def __repr__(self):
        s = super().__repr__()
        s = s.replace(">", f" {{name='{self._universe}', state={self._stream.state}}}>")
        return s

    @property
    def df(self):
        if self._data is None or self._column_names is None:
            return pd.DataFrame([])
        return pd.DataFrame.from_records(self._data, columns=self._column_names)

    def get_snapshot(self) -> pd.DataFrame:
        return self.df

    def open(self, **kwargs) -> "StreamState":
        return self._stream.open(**kwargs)

    async def open_async(self, **kwargs) -> "StreamState":
        return await self._stream.open_async(**kwargs)

    def close(self, **kwargs) -> "StreamState":
        return self._stream.close(**kwargs)

    def _do_on_stream_ack(self, stream: _RDPStream, message: dict) -> Any:
        return message["state"]

    def _do_on_stream_response(self, stream: _RDPStream, message: dict) -> Any:
        if "data" in message:
            self._data = message["data"]

        if "headers" in message:
            self._headers = message["headers"]
            self._column_names = [col["name"] for col in self._headers]

        return self._data, self._column_names

    def _do_on_stream_update(self, stream: _RDPStream, message: dict) -> Any:
        if "data" in message:
            self._data = message["data"]

        return self._data, self._column_names

    def _do_on_stream_alarm(self, stream: _RDPStream, message: dict) -> Any:
        return message["state"]
