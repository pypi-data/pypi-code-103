# coding: utf8

import asyncio
from typing import (
    Union,
    Callable,
    Iterable,
    TYPE_CHECKING,
    Tuple,
    ValuesView,
    KeysView,
    ItemsView,
)

import pandas as pd

from .streamingprice import StreamingPrice
from .._types import Strings
from ...core.session import get_valid_session
from ...delivery.stream import OMMStreamListener, StreamEvent
from ...delivery.stream import StreamStateManager, StreamStateEvent
from ...errors import ItemWasNotRequested
from ...tools import universe_arg_parser, fields_arg_parser, cached_property

if TYPE_CHECKING:
    from ...core.session import Session


def validate(name, input_values, requested_values):
    input_values = set(input_values)
    requested_values = set(requested_values)
    not_requested = input_values - requested_values
    has_not_requested = bool(not_requested)

    if has_not_requested:
        raise ItemWasNotRequested(name, not_requested, requested_values)


def get_available_fields(value_by_fields_by_inst_names):
    available_fields = set()
    for value_by_fields in value_by_fields_by_inst_names.values():
        fields = value_by_fields.keys()
        available_fields.update(fields)
    return available_fields


class StreamingPrices(StreamStateManager, OMMStreamListener["StreamingPrices"]):
    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        session: "Session" = None,
        fields: Union[str, list] = None,
        service: str = None,
        on_refresh: Callable = None,
        on_status: Callable = None,
        on_update: Callable = None,
        on_complete: Callable = None,
        extended_params: dict = None,
    ) -> None:
        session = get_valid_session(session)

        StreamStateManager.__init__(self, loop=session.loop, logger=session.logger())
        OMMStreamListener.__init__(
            self,
            loop=session.loop,
            logger=session.logger(),
            on_refresh=on_refresh,
            on_status=on_status,
            on_update=on_update,
            on_complete=on_complete,
        )

        self.universe: Strings = universe_arg_parser.get_list(universe)
        self._session = session
        self.fields: Strings = fields_arg_parser.get_list(fields or [])
        self._service = service
        self._extended_params = extended_params
        self._classname: str = f"[{self.__class__.__name__} universe={universe}]"
        self._completed = set()

    @cached_property
    def _streaming_prices_by_name(self) -> dict:
        retval = {}
        for name in self.universe:
            streaming_price = StreamingPrice(
                session=self._session,
                name=name,
                fields=self.fields,
                service=self._service,
                on_refresh=self._on_stream_refresh,
                on_status=self._on_stream_status,
                on_update=self._on_stream_update,
                on_complete=self._on_stream_complete,
                on_error=self._on_stream_error,
                extended_params=self._extended_params,
            )
            streaming_price.on(StreamStateEvent.CLOSED, self._on_stream_close)
            retval[name] = streaming_price
        return retval

    def keys(self) -> KeysView[str]:
        return self._streaming_prices_by_name.keys()

    def values(self) -> ValuesView[StreamingPrice]:
        return self._streaming_prices_by_name.values()

    def items(self) -> ItemsView[str, StreamingPrice]:
        return self._streaming_prices_by_name.items()

    def __iter__(self):
        return StreamingPricesIterator(self)

    def __getitem__(self, name) -> StreamingPrice:
        streaming_price = self._streaming_prices_by_name.get(name, {})

        if streaming_price == {}:
            self._warning(f"'{name}' not in StreamingPrices universe")

        return streaming_price

    def __len__(self):
        return len(self._streaming_prices_by_name)

    def get_snapshot(
        self, universe: Strings = None, fields: Strings = None, convert: bool = True
    ) -> pd.DataFrame:
        """
        Returns a Dataframe filled with snapshot values
        for a list of instrument names and a list of fields.

        Parameters
        ----------
        universe: list of strings
            List of instruments to request snapshot data on.

        fields: list of strings
            List of fields to request.

        convert: boolean
            If True, force numeric conversion for all values.

        Returns
        -------
            pandas.DataFrame

            pandas.DataFrame content:
                - columns : instrument and field names
                - rows : instrument name and field values

        Raises
        ------
            Exception
                If request fails or if server returns an error

            ValueError
                If a parameter type or value is wrong

        """

        if universe:
            universe = universe_arg_parser.get_list(universe)
            try:
                validate("Instrument", universe, self.universe)
            except ItemWasNotRequested as e:
                self._error(e)
                return pd.DataFrame()
        else:
            universe = self.universe

        value_by_fields_by_inst_names: dict = {}
        for name in universe:
            streaming_price: StreamingPrice = self._streaming_prices_by_name.get(name)

            values_by_fields = streaming_price.get_fields(fields)
            if values_by_fields:
                value_by_fields_by_inst_names[name] = values_by_fields

        if fields:
            try:
                validate("Field", fields, self.fields)
            except ItemWasNotRequested as e:
                self._error(e)
                return pd.DataFrame()
        else:
            fields = get_available_fields(value_by_fields_by_inst_names)

        values_by_field = {}
        for field in fields:
            values = []
            for name in universe:
                value_by_fields = value_by_fields_by_inst_names.get(name, {})
                value = value_by_fields.get(field, None)
                values.append(value)
            values_by_field[field] = values

        price_df = pd.DataFrame(values_by_field, columns=fields)

        if convert and not price_df.empty:
            price_df = price_df.convert_dtypes()

        universe_df = pd.DataFrame(universe, columns=["Instrument"])
        return pd.concat([universe_df, price_df], axis=1)

    def _do_pause(self) -> None:
        for streaming_price in self.values():
            streaming_price.pause()

    def _do_resume(self) -> None:
        for streaming_price in self.values():
            streaming_price.resume()

    async def _do_open_async(self, *args, with_updates=True) -> None:
        self._debug(f"StreamingPrices : open streaming on {self.universe}")
        self._completed.clear()
        streaming_prices_iterator = iter(self.values())

        try:
            stream_opens_socket = next(streaming_prices_iterator)
        except StopIteration:
            raise ValueError("No instrument to subscribe")

        await stream_opens_socket.open_async(*args, with_updates=with_updates)
        await asyncio.gather(
            *[
                item.open_async(*args, with_updates=with_updates)
                for item in streaming_prices_iterator
            ]
        )
        self._debug(f"StreamingPrices : streaming on {self.universe} is open")

    async def _do_close_async(self, *args, **kwargs) -> None:
        self._debug(f"StreamingPrices : close streaming on {str(self.universe)}")
        await asyncio.gather(*[item.close_async() for item in self.values()])

    def _on_stream_close(self, streaming_price: StreamingPrice) -> None:
        all_closed = all(streaming_price.is_closed for streaming_price in self.values())
        self._debug(
            f"StreamingPrices : streaming closed name={streaming_price.name}\n"
            f"\tTrying to close... all_closed={all_closed}"
        )
        if all_closed:
            self.close()

    def _do_on_stream_refresh(self, stream: StreamingPrice, *args) -> Tuple:
        fields = args[0]
        return stream.name, fields

    def _on_stream_status(self, stream: StreamingPrice, *args) -> None:
        self._debug(f"{self._classname} on_status {args}")

        status = args[0]
        self._emitter.emit(StreamEvent.STATUS, self, stream.name, status)

        if stream.is_closed:
            self.dispatch_complete(stream)

    def _do_on_stream_update(self, stream: StreamingPrice, *args) -> Tuple:
        fields = args[0]
        return stream.name, fields

    def _on_stream_complete(self, stream: StreamingPrice, *args) -> None:
        self._debug(f"{self._classname} on_complete {args}")

        name = stream.name
        if name in self._completed:
            return

        self._completed.update([name])
        if self._completed == set(self.universe):
            self._emitter.emit(StreamEvent.COMPLETE, self)

    def _do_on_stream_error(self, stream: StreamingPrice, *args) -> Tuple:
        error = args[0]
        return stream.name, error


class StreamingPricesIterator:
    def __init__(self, streaming_prices: StreamingPrices):
        self._streaming_prices = streaming_prices
        self._index = 0

    def __next__(self):
        if self._index < len(self._streaming_prices.universe):
            result = self._streaming_prices[
                self._streaming_prices.universe[self._index]
            ]
            self._index += 1
            return result
        raise StopIteration()
