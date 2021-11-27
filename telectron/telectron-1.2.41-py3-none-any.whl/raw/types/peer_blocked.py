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


class PeerBlocked(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.PeerBlocked`.

    Details:
        - Layer: ``129``
        - ID: ``0xe8fd8014``

    Parameters:
        peer_id: :obj:`Peer <telectron.raw.base.Peer>`
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer_id", "date"]

    ID = 0xe8fd8014
    QUALNAME = "types.PeerBlocked"

    def __init__(self, *, peer_id: "raw.base.Peer", date: int) -> None:
        self.peer_id = peer_id  # Peer
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "PeerBlocked":
        # No flags
        
        peer_id = TLObject.read(data)
        
        date = Int.read(data)
        
        return PeerBlocked(peer_id=peer_id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(self.peer_id.write())
        
        data.write(Int(self.date))
        
        return data.getvalue()
