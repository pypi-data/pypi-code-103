# Copyright (C) 2021 Satoshi Konno. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Bytes():
    """
    Binary defines utility functions for converting between bytes and integer.
    """

    @classmethod
    def from_int(cls, val: int, bytes_size: int) -> bytes:
        byte_buf = bytearray(bytes_size)
        for n in range(bytes_size):
            idx = (bytes_size - 1) - n
            byte_buf[idx] = ((val >> (n * 8)) & 0xFF)
        return byte_buf

    @classmethod
    def to_int(cls, byte_buf: bytes) -> int:
        val = 0
        bytes_size = len(byte_buf)
        for n in range(bytes_size):
            idx = (bytes_size - 1) - n
            val += (byte_buf[idx]) << (n * 8)
        return val

    @classmethod
    def from_string(cls, val: str) -> bytes:
        return bytes.fromhex(val)
