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


class UploadProfilePhoto(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``129``
        - ID: ``0x89f30f69``

    Parameters:
        file (optional): :obj:`InputFile <telectron.raw.base.InputFile>`
        video (optional): :obj:`InputFile <telectron.raw.base.InputFile>`
        video_start_ts (optional): ``float`` ``64-bit``

    Returns:
        :obj:`photos.Photo <telectron.raw.base.photos.Photo>`
    """

    __slots__: List[str] = ["file", "video", "video_start_ts"]

    ID = 0x89f30f69
    QUALNAME = "functions.photos.UploadProfilePhoto"

    def __init__(self, *, file: "raw.base.InputFile" = None, video: "raw.base.InputFile" = None, video_start_ts: Union[None, float] = None) -> None:
        self.file = file  # flags.0?InputFile
        self.video = video  # flags.1?InputFile
        self.video_start_ts = video_start_ts  # flags.2?double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "UploadProfilePhoto":
        flags = Int.read(data)
        
        file = TLObject.read(data) if flags & (1 << 0) else None
        
        video = TLObject.read(data) if flags & (1 << 1) else None
        
        video_start_ts = Double.read(data) if flags & (1 << 2) else None
        return UploadProfilePhoto(file=file, video=video, video_start_ts=video_start_ts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.file is not None else 0
        flags |= (1 << 1) if self.video is not None else 0
        flags |= (1 << 2) if self.video_start_ts is not None else 0
        data.write(Int(flags))
        
        if self.file is not None:
            data.write(self.file.write())
        
        if self.video is not None:
            data.write(self.video.write())
        
        if self.video_start_ts is not None:
            data.write(Double(self.video_start_ts))
        
        return data.getvalue()
