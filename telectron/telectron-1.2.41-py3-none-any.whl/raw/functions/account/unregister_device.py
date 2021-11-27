#  telectron - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2021 Dan <https://github.com/delivrance>
#
#  This file is part of telectron.
#
#  telectron is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  telectron is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with telectron.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from telectron.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from telectron.raw.core import TLObject
from telectron import raw
from typing import List, Union, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class UnregisterDevice(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0x3076c4bf``

    Parameters:
        token_type: ``int`` ``32-bit``
        token: ``str``
        other_uids: List of ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["token_type", "token", "other_uids"]

    ID = 0x3076c4bf
    QUALNAME = "functions.account.UnregisterDevice"

    def __init__(self, *, token_type: int, token: str, other_uids: List[int]) -> None:
        self.token_type = token_type  # int
        self.token = token  # string
        self.other_uids = other_uids  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "UnregisterDevice":
        # No flags
        
        token_type = Int.read(data)
        
        token = String.read(data)
        
        other_uids = TLObject.read(data, Int)
        
        return UnregisterDevice(token_type=token_type, token=token, other_uids=other_uids)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Int(self.token_type))
        
        data.write(String(self.token))
        
        data.write(Vector(self.other_uids, Int))
        
        return data.getvalue()
