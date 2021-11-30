# coding: utf8

import re
from typing import Tuple, Any

from .._content_type import ContentType
from ...core.session import get_valid_session
from ...delivery.stream import (
    StreamStateEvent,
    StreamStateManager,
    OMMStreamListener,
    _OMMStream,
)
from ...delivery.stream._stream_factory import create_omm_stream
from ...delivery.stream.stream_cache import StreamCache
from ...tools import cached_property

# regular expression pattern for intra-field position sequence
_partial_update_intra_field_positioning_sequence_regular_expression_pattern = (
    r"[\x1b\x5b|\x9b]([0-9]+)\x60([^\x1b^\x5b|^\x9b]+)"
)
_huge = 1e12


def _decode_intra_field_position_sequence(cached_value, new_value):
    # find all partial update in the value
    tokens = re.findall(
        _partial_update_intra_field_positioning_sequence_regular_expression_pattern,
        new_value,
    )

    # check this value contains a partial update or not?
    if len(tokens) == 0:
        # no partial update required, so done
        return new_value

    # do a partial update
    updated_value = cached_value
    for (offset, replace) in tokens:
        # convert offset from str to int
        offset = int(offset)
        assert offset < len(updated_value)

        # replace the value in the string
        updated_value = (
            updated_value[:offset] + replace + updated_value[offset + len(replace) :]
        )

    # done, return
    return updated_value


class StreamingPrice(
    StreamCache, StreamStateManager, OMMStreamListener["StreamingPrice"]
):
    def __init__(
        self,
        name,
        session=None,
        fields=None,
        service=None,
        extended_params=None,
        on_refresh=None,
        on_status=None,
        on_update=None,
        on_complete=None,
        on_error=None,
    ):
        if name is None:
            raise AttributeError("Instrument name must be defined.")

        session = get_valid_session(session)

        StreamCache.__init__(self, name=name, fields=fields, service=service)
        StreamStateManager.__init__(self, loop=session.loop, logger=session.logger())
        OMMStreamListener.__init__(
            self,
            loop=session.loop,
            logger=session.logger(),
            on_refresh=on_refresh,
            on_status=on_status,
            on_update=on_update,
            on_complete=on_complete,
            on_error=on_error,
        )
        self._classname: str = f"[{self.__class__.__name__} name={name}]"
        self._session = session
        self._extended_params = extended_params

    @cached_property
    def _stream(self) -> _OMMStream:
        omm_stream = create_omm_stream(
            ContentType.STREAMING_PRICING,
            session=self._session,
            name=self._name,
            domain="MarketPrice",
            service=self._service,
            fields=self._fields,
            extended_params=self._extended_params,
            on_refresh=self._on_stream_refresh,
            on_status=self._on_stream_status,
            on_update=self._on_stream_update,
            on_complete=self._on_stream_complete,
            on_error=self._on_stream_error,
        )
        omm_stream.on(StreamStateEvent.CLOSED, self.close)
        return omm_stream

    @property
    def id(self) -> int:
        return self._stream.id

    @property
    def code(self):
        return self._stream.code

    @property
    def message(self):
        return self._stream.message

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def _do_pause(self):
        self._stream.pause()

    def _do_resume(self):
        self._stream.resume()

    async def _do_close_async(self, *args, **kwargs):
        id_ = self._stream.id
        self._debug(f"Stop StreamingPrice subscription {id_} to {self.name}")
        await self._stream.close_async(*args, **kwargs)

    async def _do_open_async(self, *args, with_updates=True):
        id_ = self._stream.id
        self._debug(f"Open async StreamingPrice {id_} to {self.name}")
        await self._stream.open_async(*args, with_updates=with_updates)

    def _decode_partial_update_field(self, key, value):
        """
        This legacy is used to process the partial update
        RETURNS the processed partial update data
        """

        fields = self._record.get("Fields")
        if key not in fields:
            fields[key] = value
            self._warning(f"key {key} not in self._record['Fields']")
            return value

        # process infra-field positioning sequence
        cached_value = fields[key]
        updated_value = _decode_intra_field_position_sequence(cached_value, value)

        # done
        return updated_value

    def _write_to_record(self, message: dict):
        for data in message:
            if data == "Fields":
                # fields data
                # loop over all update items
                for key, value in message[data].items():
                    # only string value need to check for a partial update
                    if isinstance(value, str):
                        # value is a string, so check for partial update string
                        # process partial update and update the callback
                        # with processed partial update
                        message[data][key] = self._decode_partial_update_field(
                            key, value
                        )

                # update the field data
                self._record[data].update(message[data])
            else:
                # not a "Fields" data
                self._record[data] = message[data]

    def _do_on_stream_refresh(self, stream: "_OMMStream", *args) -> Tuple:
        message = args[0]
        self._record = message
        fields = message.get("Fields")
        return fields

    def _do_on_stream_status(self, stream: "_OMMStream", *args) -> Any:
        message = args[0]
        self._status = message
        return message

    def _do_on_stream_update(self, stream: "_OMMStream", *args) -> Any:
        message = args[0]
        self._record = message
        self._write_to_record(message)
        fields = message.get("Fields")
        return fields

    def _do_on_stream_error(self, originator, *args) -> Any:
        if self.is_open:
            self.dispatch_complete(originator, *args)

        return args
