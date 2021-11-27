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


class CheckHistoryImportPeer(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0x5dc60f03``

    Parameters:
        peer: :obj:`InputPeer <telectron.raw.base.InputPeer>`

    Returns:
        :obj:`messages.CheckedHistoryImportPeer <telectron.raw.base.messages.CheckedHistoryImportPeer>`
    """

    __slots__: List[str] = ["peer"]

    ID = 0x5dc60f03
    QUALNAME = "functions.messages.CheckHistoryImportPeer"

    def __init__(self, *, peer: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "CheckHistoryImportPeer":
        # No flags
        
        peer = TLObject.read(data)
        
        return CheckHistoryImportPeer(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
