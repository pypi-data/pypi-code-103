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


class DiscussionMessage(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.DiscussionMessage`.

    Details:
        - Layer: ``129``
        - ID: ``0xf5dd8f9d``

    Parameters:
        messages: List of :obj:`Message <telectron.raw.base.Message>`
        chats: List of :obj:`Chat <telectron.raw.base.Chat>`
        users: List of :obj:`User <telectron.raw.base.User>`
        max_id (optional): ``int`` ``32-bit``
        read_inbox_max_id (optional): ``int`` ``32-bit``
        read_outbox_max_id (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDiscussionMessage <telectron.raw.functions.messages.GetDiscussionMessage>`
    """

    __slots__: List[str] = ["messages", "chats", "users", "max_id", "read_inbox_max_id", "read_outbox_max_id"]

    ID = 0xf5dd8f9d
    QUALNAME = "types.messages.DiscussionMessage"

    def __init__(self, *, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], max_id: Union[None, int] = None, read_inbox_max_id: Union[None, int] = None, read_outbox_max_id: Union[None, int] = None) -> None:
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.max_id = max_id  # flags.0?int
        self.read_inbox_max_id = read_inbox_max_id  # flags.1?int
        self.read_outbox_max_id = read_outbox_max_id  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "DiscussionMessage":
        flags = Int.read(data)
        
        messages = TLObject.read(data)
        
        max_id = Int.read(data) if flags & (1 << 0) else None
        read_inbox_max_id = Int.read(data) if flags & (1 << 1) else None
        read_outbox_max_id = Int.read(data) if flags & (1 << 2) else None
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return DiscussionMessage(messages=messages, chats=chats, users=users, max_id=max_id, read_inbox_max_id=read_inbox_max_id, read_outbox_max_id=read_outbox_max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.max_id is not None else 0
        flags |= (1 << 1) if self.read_inbox_max_id is not None else 0
        flags |= (1 << 2) if self.read_outbox_max_id is not None else 0
        data.write(Int(flags))
        
        data.write(Vector(self.messages))
        
        if self.max_id is not None:
            data.write(Int(self.max_id))
        
        if self.read_inbox_max_id is not None:
            data.write(Int(self.read_inbox_max_id))
        
        if self.read_outbox_max_id is not None:
            data.write(Int(self.read_outbox_max_id))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
