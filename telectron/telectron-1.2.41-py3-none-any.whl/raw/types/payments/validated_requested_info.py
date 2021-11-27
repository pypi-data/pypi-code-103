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


class ValidatedRequestedInfo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.payments.ValidatedRequestedInfo`.

    Details:
        - Layer: ``129``
        - ID: ``0xd1451883``

    Parameters:
        id (optional): ``str``
        shipping_options (optional): List of :obj:`ShippingOption <telectron.raw.base.ShippingOption>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.ValidateRequestedInfo <telectron.raw.functions.payments.ValidateRequestedInfo>`
    """

    __slots__: List[str] = ["id", "shipping_options"]

    ID = 0xd1451883
    QUALNAME = "types.payments.ValidatedRequestedInfo"

    def __init__(self, *, id: Union[None, str] = None, shipping_options: Union[None, List["raw.base.ShippingOption"]] = None) -> None:
        self.id = id  # flags.0?string
        self.shipping_options = shipping_options  # flags.1?Vector<ShippingOption>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "ValidatedRequestedInfo":
        flags = Int.read(data)
        
        id = String.read(data) if flags & (1 << 0) else None
        shipping_options = TLObject.read(data) if flags & (1 << 1) else []
        
        return ValidatedRequestedInfo(id=id, shipping_options=shipping_options)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.id is not None else 0
        flags |= (1 << 1) if self.shipping_options is not None else 0
        data.write(Int(flags))
        
        if self.id is not None:
            data.write(String(self.id))
        
        if self.shipping_options is not None:
            data.write(Vector(self.shipping_options))
        
        return data.getvalue()
