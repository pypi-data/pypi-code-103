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


class UpdateGroupCallParticipants(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.Update`.

    Details:
        - Layer: ``129``
        - ID: ``0xf2ebdb4e``

    Parameters:
        call: :obj:`InputGroupCall <telectron.raw.base.InputGroupCall>`
        participants: List of :obj:`GroupCallParticipant <telectron.raw.base.GroupCallParticipant>`
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "participants", "version"]

    ID = 0xf2ebdb4e
    QUALNAME = "types.UpdateGroupCallParticipants"

    def __init__(self, *, call: "raw.base.InputGroupCall", participants: List["raw.base.GroupCallParticipant"], version: int) -> None:
        self.call = call  # InputGroupCall
        self.participants = participants  # Vector<GroupCallParticipant>
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "UpdateGroupCallParticipants":
        # No flags
        
        call = TLObject.read(data)
        
        participants = TLObject.read(data)
        
        version = Int.read(data)
        
        return UpdateGroupCallParticipants(call=call, participants=participants, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.participants))
        
        data.write(Int(self.version))
        
        return data.getvalue()
