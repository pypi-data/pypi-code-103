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


class GroupCall(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.GroupCall`.

    Details:
        - Layer: ``129``
        - ID: ``0x653dbaad``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        participants_count: ``int`` ``32-bit``
        version: ``int`` ``32-bit``
        join_muted (optional): ``bool``
        can_change_join_muted (optional): ``bool``
        join_date_asc (optional): ``bool``
        schedule_start_subscribed (optional): ``bool``
        can_start_video (optional): ``bool``
        title (optional): ``str``
        stream_dc_id (optional): ``int`` ``32-bit``
        record_start_date (optional): ``int`` ``32-bit``
        schedule_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "participants_count", "version", "join_muted", "can_change_join_muted", "join_date_asc", "schedule_start_subscribed", "can_start_video", "title", "stream_dc_id", "record_start_date", "schedule_date"]

    ID = 0x653dbaad
    QUALNAME = "types.GroupCall"

    def __init__(self, *, id: int, access_hash: int, participants_count: int, version: int, join_muted: Union[None, bool] = None, can_change_join_muted: Union[None, bool] = None, join_date_asc: Union[None, bool] = None, schedule_start_subscribed: Union[None, bool] = None, can_start_video: Union[None, bool] = None, title: Union[None, str] = None, stream_dc_id: Union[None, int] = None, record_start_date: Union[None, int] = None, schedule_date: Union[None, int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.participants_count = participants_count  # int
        self.version = version  # int
        self.join_muted = join_muted  # flags.1?true
        self.can_change_join_muted = can_change_join_muted  # flags.2?true
        self.join_date_asc = join_date_asc  # flags.6?true
        self.schedule_start_subscribed = schedule_start_subscribed  # flags.8?true
        self.can_start_video = can_start_video  # flags.9?true
        self.title = title  # flags.3?string
        self.stream_dc_id = stream_dc_id  # flags.4?int
        self.record_start_date = record_start_date  # flags.5?int
        self.schedule_date = schedule_date  # flags.7?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "GroupCall":
        flags = Int.read(data)
        
        join_muted = True if flags & (1 << 1) else False
        can_change_join_muted = True if flags & (1 << 2) else False
        join_date_asc = True if flags & (1 << 6) else False
        schedule_start_subscribed = True if flags & (1 << 8) else False
        can_start_video = True if flags & (1 << 9) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        participants_count = Int.read(data)
        
        title = String.read(data) if flags & (1 << 3) else None
        stream_dc_id = Int.read(data) if flags & (1 << 4) else None
        record_start_date = Int.read(data) if flags & (1 << 5) else None
        schedule_date = Int.read(data) if flags & (1 << 7) else None
        version = Int.read(data)
        
        return GroupCall(id=id, access_hash=access_hash, participants_count=participants_count, version=version, join_muted=join_muted, can_change_join_muted=can_change_join_muted, join_date_asc=join_date_asc, schedule_start_subscribed=schedule_start_subscribed, can_start_video=can_start_video, title=title, stream_dc_id=stream_dc_id, record_start_date=record_start_date, schedule_date=schedule_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.join_muted else 0
        flags |= (1 << 2) if self.can_change_join_muted else 0
        flags |= (1 << 6) if self.join_date_asc else 0
        flags |= (1 << 8) if self.schedule_start_subscribed else 0
        flags |= (1 << 9) if self.can_start_video else 0
        flags |= (1 << 3) if self.title is not None else 0
        flags |= (1 << 4) if self.stream_dc_id is not None else 0
        flags |= (1 << 5) if self.record_start_date is not None else 0
        flags |= (1 << 7) if self.schedule_date is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.participants_count))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.stream_dc_id is not None:
            data.write(Int(self.stream_dc_id))
        
        if self.record_start_date is not None:
            data.write(Int(self.record_start_date))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        data.write(Int(self.version))
        
        return data.getvalue()
