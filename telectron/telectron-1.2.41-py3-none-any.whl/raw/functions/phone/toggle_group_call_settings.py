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


class ToggleGroupCallSettings(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0x74bbb43d``

    Parameters:
        call: :obj:`InputGroupCall <telectron.raw.base.InputGroupCall>`
        reset_invite_hash (optional): ``bool``
        join_muted (optional): ``bool``

    Returns:
        :obj:`Updates <telectron.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "reset_invite_hash", "join_muted"]

    ID = 0x74bbb43d
    QUALNAME = "functions.phone.ToggleGroupCallSettings"

    def __init__(self, *, call: "raw.base.InputGroupCall", reset_invite_hash: Union[None, bool] = None, join_muted: Union[None, bool] = None) -> None:
        self.call = call  # InputGroupCall
        self.reset_invite_hash = reset_invite_hash  # flags.1?true
        self.join_muted = join_muted  # flags.0?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "ToggleGroupCallSettings":
        flags = Int.read(data)
        
        reset_invite_hash = True if flags & (1 << 1) else False
        call = TLObject.read(data)
        
        join_muted = Bool.read(data) if flags & (1 << 0) else None
        return ToggleGroupCallSettings(call=call, reset_invite_hash=reset_invite_hash, join_muted=join_muted)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.reset_invite_hash else 0
        flags |= (1 << 0) if self.join_muted is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        if self.join_muted is not None:
            data.write(Bool(self.join_muted))
        
        return data.getvalue()
