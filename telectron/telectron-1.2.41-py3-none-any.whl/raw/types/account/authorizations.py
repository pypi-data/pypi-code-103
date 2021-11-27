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


class Authorizations(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.account.Authorizations`.

    Details:
        - Layer: ``129``
        - ID: ``0x1250abde``

    Parameters:
        authorizations: List of :obj:`Authorization <telectron.raw.base.Authorization>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAuthorizations <telectron.raw.functions.account.GetAuthorizations>`
    """

    __slots__: List[str] = ["authorizations"]

    ID = 0x1250abde
    QUALNAME = "types.account.Authorizations"

    def __init__(self, *, authorizations: List["raw.base.Authorization"]) -> None:
        self.authorizations = authorizations  # Vector<Authorization>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "Authorizations":
        # No flags
        
        authorizations = TLObject.read(data)
        
        return Authorizations(authorizations=authorizations)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(Vector(self.authorizations))
        
        return data.getvalue()
