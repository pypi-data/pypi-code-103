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


class EmojiKeywordsDifference(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.EmojiKeywordsDifference`.

    Details:
        - Layer: ``129``
        - ID: ``0x5cc761bd``

    Parameters:
        lang_code: ``str``
        from_version: ``int`` ``32-bit``
        version: ``int`` ``32-bit``
        keywords: List of :obj:`EmojiKeyword <telectron.raw.base.EmojiKeyword>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiKeywords <telectron.raw.functions.messages.GetEmojiKeywords>`
            - :obj:`messages.GetEmojiKeywordsDifference <telectron.raw.functions.messages.GetEmojiKeywordsDifference>`
    """

    __slots__: List[str] = ["lang_code", "from_version", "version", "keywords"]

    ID = 0x5cc761bd
    QUALNAME = "types.EmojiKeywordsDifference"

    def __init__(self, *, lang_code: str, from_version: int, version: int, keywords: List["raw.base.EmojiKeyword"]) -> None:
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int
        self.version = version  # int
        self.keywords = keywords  # Vector<EmojiKeyword>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "EmojiKeywordsDifference":
        # No flags
        
        lang_code = String.read(data)
        
        from_version = Int.read(data)
        
        version = Int.read(data)
        
        keywords = TLObject.read(data)
        
        return EmojiKeywordsDifference(lang_code=lang_code, from_version=from_version, version=version, keywords=keywords)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.from_version))
        
        data.write(Int(self.version))
        
        data.write(Vector(self.keywords))
        
        return data.getvalue()
