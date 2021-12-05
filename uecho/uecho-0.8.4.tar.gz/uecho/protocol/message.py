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

from typing import List, Tuple, Any, Optional
from ..util.bytes import Bytes
from .esv import ESV
from .property import Property


class Message(ESV):
    """
    Message represents a protocol message of Echonet Lite.
    """
    FRAME_HEADER_SIZE = (1 + 1 + 2)
    FORMAT1_HEADER_SIZE = (3 + 3 + 1 + 1)
    FORMAT1_MIN_SIZE = (FRAME_HEADER_SIZE + FORMAT1_HEADER_SIZE)
    FORMAT1_PROPERTY_HEADER_SIZE = 2
    EHD1_ECHONET = 0x10
    EHD2_FORMAT1 = 0x81
    TID_SIZE = 2
    TID_MAX = 65535
    EOJ_SIZE = 3

    class ParserError(Exception):
        pass

    TID: int
    SEOJ: int
    DEOJ: int
    properties: List[Property]
    from_addr: Optional[Tuple[str, int]]
    to_addr: Optional[Tuple[str, int]]

    def __init__(self):
        super().__init__()
        self.TID = 0
        self.SEOJ = 0
        self.DEOJ = 0
        self.properties = []
        self.from_addr = None
        self.to_addr = None

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.to_bytes() == other.to_bytes()
        return False

    @property
    def OPC(self) -> int:
        return len(self.properties)

    def add_property(self, prop: Any) -> bool:
        if not isinstance(prop, Property):
            return False
        self.properties.append(prop)
        return True

    def is_response(self, msg):
        if self.TID != msg.TID:
            return False
        return True

    def parse_bytes(self, msg_bytes) -> bool:
        # Frame heade
        if len(msg_bytes) < Message.FORMAT1_HEADER_SIZE:
            raise Message.ParserError()
        if msg_bytes[0] != Message.EHD1_ECHONET:
            raise Message.ParserError()
        if msg_bytes[1] != Message.EHD2_FORMAT1:
            raise Message.ParserError()
        self.TID = Bytes.to_int(msg_bytes[2:4])

        # Echonet Format1 Header
        self.SEOJ = Bytes.to_int(msg_bytes[4:7])
        self.DEOJ = Bytes.to_int(msg_bytes[7:10])
        self.ESV = msg_bytes[10]

        # Propety data
        opc = msg_bytes[11]
        offset = 12
        for n in range(opc):
            if len(msg_bytes) < (offset + 1):
                raise Message.ParserError()
            prop = Property()
            prop.code = msg_bytes[offset]
            offset += 1
            pdc = msg_bytes[offset]
            offset += 1
            if len(msg_bytes) < (offset + pdc):
                raise Message.ParserError()
            prop.data = msg_bytes[offset:(offset + pdc)]
            self.properties.append(prop)
            offset += pdc

        return True

    def parse_hexstring(self, hes_string: str) -> bool:
        return self.parse_bytes(Bytes.from_string(hes_string))

    def to_bytes(self) -> bytes:
        msg_bytes = bytearray([Message.EHD1_ECHONET, Message.EHD2_FORMAT1])
        msg_bytes.extend(Bytes.from_int(self.TID, 2))
        msg_bytes.extend(Bytes.from_int(self.SEOJ, 3))
        msg_bytes.extend(Bytes.from_int(self.DEOJ, 3))
        msg_bytes.append(self.ESV)

        msg_bytes.append(len(self.properties))
        for prop in self.properties:
            msg_bytes.append(prop.code)
            msg_bytes.append(len(prop.data))
            msg_bytes.extend(prop.data)

        return msg_bytes

    def to_string(self) -> str:
        return self.to_bytes().hex().upper()
