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


class BotInfo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.BotInfo`.

    Details:
        - Layer: ``129``
        - ID: ``0x98e81d3a``

    Parameters:
        user_id: ``int`` ``32-bit``
        description: ``str``
        commands: List of :obj:`BotCommand <telectron.raw.base.BotCommand>`
    """

    __slots__: List[str] = ["user_id", "description", "commands"]

    ID = 0x98e81d3a
    QUALNAME = "types.BotInfo"

    def __init__(self, *, user_id: int, description: str, commands: List["raw.base.BotCommand"]) -> None:
        self.user_id = user_id  # int
        self.description = description  # string
        self.commands = commands  # Vector<BotCommand>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "BotInfo":
        # No flags
        
        user_id = Int.read(data)
        
        description = String.read(data)
        
        commands = TLObject.read(data)
        
        return BotInfo(user_id=user_id, description=description, commands=commands)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Int(self.user_id))
        
        data.write(String(self.description))
        
        data.write(Vector(self.commands))
        
        return data.getvalue()
