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


class EditInlineBotMessage(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0x83557dba``

    Parameters:
        id: :obj:`InputBotInlineMessageID <telectron.raw.base.InputBotInlineMessageID>`
        no_webpage (optional): ``bool``
        message (optional): ``str``
        media (optional): :obj:`InputMedia <telectron.raw.base.InputMedia>`
        reply_markup (optional): :obj:`ReplyMarkup <telectron.raw.base.ReplyMarkup>`
        entities (optional): List of :obj:`MessageEntity <telectron.raw.base.MessageEntity>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "no_webpage", "message", "media", "reply_markup", "entities"]

    ID = 0x83557dba
    QUALNAME = "functions.messages.EditInlineBotMessage"

    def __init__(self, *, id: "raw.base.InputBotInlineMessageID", no_webpage: Union[None, bool] = None, message: Union[None, str] = None, media: "raw.base.InputMedia" = None, reply_markup: "raw.base.ReplyMarkup" = None, entities: Union[None, List["raw.base.MessageEntity"]] = None) -> None:
        self.id = id  # InputBotInlineMessageID
        self.no_webpage = no_webpage  # flags.1?true
        self.message = message  # flags.11?string
        self.media = media  # flags.14?InputMedia
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup
        self.entities = entities  # flags.3?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "EditInlineBotMessage":
        flags = Int.read(data)
        
        no_webpage = True if flags & (1 << 1) else False
        id = TLObject.read(data)
        
        message = String.read(data) if flags & (1 << 11) else None
        media = TLObject.read(data) if flags & (1 << 14) else None
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        entities = TLObject.read(data) if flags & (1 << 3) else []
        
        return EditInlineBotMessage(id=id, no_webpage=no_webpage, message=message, media=media, reply_markup=reply_markup, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.no_webpage else 0
        flags |= (1 << 11) if self.message is not None else 0
        flags |= (1 << 14) if self.media is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        flags |= (1 << 3) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        if self.message is not None:
            data.write(String(self.message))
        
        if self.media is not None:
            data.write(self.media.write())
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
