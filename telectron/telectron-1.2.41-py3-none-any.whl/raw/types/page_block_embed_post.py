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


class PageBlockEmbedPost(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.PageBlock`.

    Details:
        - Layer: ``129``
        - ID: ``0xf259a80b``

    Parameters:
        url: ``str``
        webpage_id: ``int`` ``64-bit``
        author_photo_id: ``int`` ``64-bit``
        author: ``str``
        date: ``int`` ``32-bit``
        blocks: List of :obj:`PageBlock <telectron.raw.base.PageBlock>`
        caption: :obj:`PageCaption <telectron.raw.base.PageCaption>`
    """

    __slots__: List[str] = ["url", "webpage_id", "author_photo_id", "author", "date", "blocks", "caption"]

    ID = 0xf259a80b
    QUALNAME = "types.PageBlockEmbedPost"

    def __init__(self, *, url: str, webpage_id: int, author_photo_id: int, author: str, date: int, blocks: List["raw.base.PageBlock"], caption: "raw.base.PageCaption") -> None:
        self.url = url  # string
        self.webpage_id = webpage_id  # long
        self.author_photo_id = author_photo_id  # long
        self.author = author  # string
        self.date = date  # int
        self.blocks = blocks  # Vector<PageBlock>
        self.caption = caption  # PageCaption

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "PageBlockEmbedPost":
        # No flags
        
        url = String.read(data)
        
        webpage_id = Long.read(data)
        
        author_photo_id = Long.read(data)
        
        author = String.read(data)
        
        date = Int.read(data)
        
        blocks = TLObject.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockEmbedPost(url=url, webpage_id=webpage_id, author_photo_id=author_photo_id, author=author, date=date, blocks=blocks, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Long(self.webpage_id))
        
        data.write(Long(self.author_photo_id))
        
        data.write(String(self.author))
        
        data.write(Int(self.date))
        
        data.write(Vector(self.blocks))
        
        data.write(self.caption.write())
        
        return data.getvalue()
