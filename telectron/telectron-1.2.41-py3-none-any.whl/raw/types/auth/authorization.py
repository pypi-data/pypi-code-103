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


class Authorization(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.auth.Authorization`.

    Details:
        - Layer: ``129``
        - ID: ``0xcd050916``

    Parameters:
        user: :obj:`User <telectron.raw.base.User>`
        tmp_sessions (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.SignUp <telectron.raw.functions.auth.SignUp>`
            - :obj:`auth.SignIn <telectron.raw.functions.auth.SignIn>`
            - :obj:`auth.ImportAuthorization <telectron.raw.functions.auth.ImportAuthorization>`
            - :obj:`auth.ImportBotAuthorization <telectron.raw.functions.auth.ImportBotAuthorization>`
            - :obj:`auth.CheckPassword <telectron.raw.functions.auth.CheckPassword>`
            - :obj:`auth.RecoverPassword <telectron.raw.functions.auth.RecoverPassword>`
    """

    __slots__: List[str] = ["user", "tmp_sessions"]

    ID = 0xcd050916
    QUALNAME = "types.auth.Authorization"

    def __init__(self, *, user: "raw.base.User", tmp_sessions: Union[None, int] = None) -> None:
        self.user = user  # User
        self.tmp_sessions = tmp_sessions  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "Authorization":
        flags = Int.read(data)
        
        tmp_sessions = Int.read(data) if flags & (1 << 0) else None
        user = TLObject.read(data)
        
        return Authorization(user=user, tmp_sessions=tmp_sessions)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.tmp_sessions is not None else 0
        data.write(Int(flags))
        
        if self.tmp_sessions is not None:
            data.write(Int(self.tmp_sessions))
        
        data.write(self.user.write())
        
        return data.getvalue()
