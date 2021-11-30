from typing import Union, TYPE_CHECKING

from .open_state import stream_state_to_open_state

if TYPE_CHECKING:
    from ...content.ipa.contracts.quantitative_data_stream import QuantitativeDataStream
    from ...content.streaming.trade_data_service import TradeDataStream
    from ...content.chain.streaming_chain import StreamingChain
    from . import StreamState, OMMStream, RDPStream
    from ...content.streaming import StreamingPrices
    from .open_state import OpenState

    Stream = Union[
        StreamingPrices,
        StreamingChain,
        TradeDataStream,
        RDPStream,
        OMMStream,
        QuantitativeDataStream,
    ]


class StreamOpenStateMixin(object):
    _stream: "Stream" = None

    @staticmethod
    def _convert_state(state: "StreamState") -> "OpenState":
        return stream_state_to_open_state[state]

    @property
    def open_state(self) -> "OpenState":
        state: "StreamState" = self._stream.state
        state: "OpenState" = stream_state_to_open_state.get(state)
        return state

    def open(self, with_updates: bool = True) -> "OpenState":
        state = self._stream.open(with_updates=with_updates)
        return self._convert_state(state)

    async def open_async(self, with_updates: bool = True) -> "OpenState":
        state = await self._stream.open_async(with_updates=with_updates)
        return self._convert_state(state)

    def close(self) -> "OpenState":
        state = self._stream.close()
        return self._convert_state(state)
