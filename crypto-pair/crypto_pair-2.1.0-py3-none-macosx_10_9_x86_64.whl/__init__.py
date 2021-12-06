from enum import IntEnum
from typing import Optional

from crypto_pair._lowlevel import ffi, lib


class MarketType(IntEnum):
    '''Market type.'''
    spot = lib.Spot
    linear_future = lib.LinearFuture
    inverse_future = lib.InverseFuture
    linear_swap = lib.LinearSwap
    inverse_swap = lib.InverseSwap

    american_option = lib.AmericanOption
    european_option = lib.EuropeanOption

    quanto_future = lib.QuantoFuture
    quanto_swap = lib.QuantoSwap

    move = lib.Move
    bvol = lib.BVOL


def normalize_pair(symbol: str, exchange: str) -> Optional[str]:
    string_ptr = lib.normalize_pair(
        ffi.new("char[]", symbol.encode("utf-8")),
        ffi.new("char[]", exchange.encode("utf-8")),
    )
    if string_ptr == ffi.NULL:
        return None
    try:
        # Copy the data to a python string
        return ffi.string(string_ptr).decode('UTF-8')
    finally:
        lib.deallocate_string(string_ptr)


def get_market_type(symbol: str,
                    exchange: str,
                    is_spot: bool = False) -> MarketType:
    market_type = lib.get_market_type(
        ffi.new("char[]", symbol.encode("utf-8")),
        ffi.new("char[]", exchange.encode("utf-8")),
        ffi.cast("bool", is_spot),
    )
    return MarketType(market_type)
