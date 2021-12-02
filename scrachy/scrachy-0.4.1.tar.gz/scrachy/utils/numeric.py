#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules
import ctypes

# 3rd Party Modules

# Project Modules


def slice_int(bt: bytes, nbits: int) -> int:
    """
    Take the first ``nbits`` of ``bt`` and convert that into an integer.

    From: https://stackoverflow.com/a/47086786/4971706

    :param bt: The bytes of arbitrary length.
    :param nbits: The number of bits to keep.
    :return: The resulting integer.
    """
    # Directly convert enough bytes to an int to ensure you have at least as many bits
    # as needed, but no more
    n_bytes = len(bt)
    neededbytes = (nbits + 7) // 8

    if neededbytes > n_bytes:
        raise ValueError(f"Require {neededbytes} bytes, received {len(bt)}")

    i = int.from_bytes(bt[:neededbytes], 'big')

    # If there were a non-byte aligned number of bits requested,
    # shift off the excess from the right (which came from the last byte processed)
    if nbits % 8:
        i >>= 8 - nbits % 8

    return i


def to_int64(unsigned: int) -> int:
    """
    Convert an unsigned integer into a signed 64 bit integer.

    :param unsigned: An unsigned integer.
    :return: The signed value of the integer.
    """
    return None if unsigned is None else ctypes.c_longlong(unsigned).value


def to_uint64(signed: int) -> int:
    """
    Convert a signed (64 bit) integer into an unsigned 64 bit integer.

    :param signed: A signed integer.
    :return: The unsigned representation of the signed integer.
    """
    return None if signed is None else ctypes.c_ulonglong(signed).value
