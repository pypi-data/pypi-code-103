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


class GetBroadcastStats(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0xab42441a``

    Parameters:
        channel: :obj:`InputChannel <telectron.raw.base.InputChannel>`
        dark (optional): ``bool``

    Returns:
        :obj:`stats.BroadcastStats <telectron.raw.base.stats.BroadcastStats>`
    """

    __slots__: List[str] = ["channel", "dark"]

    ID = 0xab42441a
    QUALNAME = "functions.stats.GetBroadcastStats"

    def __init__(self, *, channel: "raw.base.InputChannel", dark: Union[None, bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.dark = dark  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "GetBroadcastStats":
        flags = Int.read(data)
        
        dark = True if flags & (1 << 0) else False
        channel = TLObject.read(data)
        
        return GetBroadcastStats(channel=channel, dark=dark)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        return data.getvalue()
