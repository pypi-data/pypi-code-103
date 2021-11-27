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


class TermsOfServiceUpdate(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.help.TermsOfServiceUpdate`.

    Details:
        - Layer: ``129``
        - ID: ``0x28ecf961``

    Parameters:
        expires: ``int`` ``32-bit``
        terms_of_service: :obj:`help.TermsOfService <telectron.raw.base.help.TermsOfService>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetTermsOfServiceUpdate <telectron.raw.functions.help.GetTermsOfServiceUpdate>`
    """

    __slots__: List[str] = ["expires", "terms_of_service"]

    ID = 0x28ecf961
    QUALNAME = "types.help.TermsOfServiceUpdate"

    def __init__(self, *, expires: int, terms_of_service: "raw.base.help.TermsOfService") -> None:
        self.expires = expires  # int
        self.terms_of_service = terms_of_service  # help.TermsOfService

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "TermsOfServiceUpdate":
        # No flags
        
        expires = Int.read(data)
        
        terms_of_service = TLObject.read(data)
        
        return TermsOfServiceUpdate(expires=expires, terms_of_service=terms_of_service)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Int(self.expires))
        
        data.write(self.terms_of_service.write())
        
        return data.getvalue()
