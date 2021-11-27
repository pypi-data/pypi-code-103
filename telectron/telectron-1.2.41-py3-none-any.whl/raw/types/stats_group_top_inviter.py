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


class StatsGroupTopInviter(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.StatsGroupTopInviter`.

    Details:
        - Layer: ``129``
        - ID: ``0x31962a4c``

    Parameters:
        user_id: ``int`` ``32-bit``
        invitations: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "invitations"]

    ID = 0x31962a4c
    QUALNAME = "types.StatsGroupTopInviter"

    def __init__(self, *, user_id: int, invitations: int) -> None:
        self.user_id = user_id  # int
        self.invitations = invitations  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "StatsGroupTopInviter":
        # No flags
        
        user_id = Int.read(data)
        
        invitations = Int.read(data)
        
        return StatsGroupTopInviter(user_id=user_id, invitations=invitations)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Int(self.user_id))
        
        data.write(Int(self.invitations))
        
        return data.getvalue()
