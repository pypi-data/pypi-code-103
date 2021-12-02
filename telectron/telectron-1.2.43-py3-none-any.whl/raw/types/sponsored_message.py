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


class SponsoredMessage(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.SponsoredMessage`.

    Details:
        - Layer: ``134``
        - ID: ``0xd151e19a``

    Parameters:
        random_id: ``bytes``
        from_id: :obj:`Peer <telectron.raw.base.Peer>`
        message: ``str``
        channel_post (optional): ``int`` ``32-bit``
        start_param (optional): ``str``
        entities (optional): List of :obj:`MessageEntity <telectron.raw.base.MessageEntity>`
    """

    __slots__: List[str] = ["random_id", "from_id", "message", "channel_post", "start_param", "entities"]

    ID = 0xd151e19a
    QUALNAME = "types.SponsoredMessage"

    def __init__(self, *, random_id: bytes, from_id: "raw.base.Peer", message: str, channel_post: Union[None, int] = None, start_param: Union[None, str] = None, entities: Union[None, List["raw.base.MessageEntity"]] = None) -> None:
        self.random_id = random_id  # bytes
        self.from_id = from_id  # Peer
        self.message = message  # string
        self.channel_post = channel_post  # flags.2?int
        self.start_param = start_param  # flags.0?string
        self.entities = entities  # flags.1?Vector<MessageEntity>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SponsoredMessage":
        flags = Int.read(b)
        
        random_id = Bytes.read(b)
        
        from_id = TLObject.read(b)
        
        channel_post = Int.read(b) if flags & (1 << 2) else None
        start_param = String.read(b) if flags & (1 << 0) else None
        message = String.read(b)
        
        entities = TLObject.read(b) if flags & (1 << 1) else []
        
        return SponsoredMessage(random_id=random_id, from_id=from_id, message=message, channel_post=channel_post, start_param=start_param, entities=entities)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 2) if self.channel_post is not None else 0
        flags |= (1 << 0) if self.start_param is not None else 0
        flags |= (1 << 1) if self.entities is not None else 0
        b.write(Int(flags))
        
        b.write(Bytes(self.random_id))
        
        b.write(self.from_id.write())
        
        if self.channel_post is not None:
            b.write(Int(self.channel_post))
        
        if self.start_param is not None:
            b.write(String(self.start_param))
        
        b.write(String(self.message))
        
        if self.entities is not None:
            b.write(Vector(self.entities))
        
        return b.getvalue()