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


class PhoneCall(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.phone.PhoneCall`.

    Details:
        - Layer: ``129``
        - ID: ``0xec82e140``

    Parameters:
        phone_call: :obj:`PhoneCall <telectron.raw.base.PhoneCall>`
        users: List of :obj:`User <telectron.raw.base.User>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`phone.RequestCall <telectron.raw.functions.phone.RequestCall>`
            - :obj:`phone.AcceptCall <telectron.raw.functions.phone.AcceptCall>`
            - :obj:`phone.ConfirmCall <telectron.raw.functions.phone.ConfirmCall>`
    """

    __slots__: List[str] = ["phone_call", "users"]

    ID = 0xec82e140
    QUALNAME = "types.phone.PhoneCall"

    def __init__(self, *, phone_call: "raw.base.PhoneCall", users: List["raw.base.User"]) -> None:
        self.phone_call = phone_call  # PhoneCall
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "PhoneCall":
        # No flags
        
        phone_call = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return PhoneCall(phone_call=phone_call, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        # No flags
        
        data.write(self.phone_call.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()
