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


class Stickers(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.Stickers`.

    Details:
        - Layer: ``129``
        - ID: ``0xe4599bbd``

    Parameters:
        hash: ``int`` ``32-bit``
        stickers: List of :obj:`Document <telectron.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickers <telectron.raw.functions.messages.GetStickers>`
    """

    __slots__: List[str] = ["hash", "stickers"]

    ID = 0xe4599bbd
    QUALNAME = "types.messages.Stickers"

    def __init__(self, *, hash: int, stickers: List["raw.base.Document"]) -> None:
        self.hash = hash  # int
        self.stickers = stickers  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "Stickers":
        # No flags
        
        hash = Int.read(data)
        
        stickers = TLObject.read(data)
        
        return Stickers(hash=hash, stickers=stickers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Int(self.hash))
        
        data.write(Vector(self.stickers))
        
        return data.getvalue()
