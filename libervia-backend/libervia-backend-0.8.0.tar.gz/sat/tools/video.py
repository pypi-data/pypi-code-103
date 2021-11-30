#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Methods to manipulate videos"""
from typing import Union
from pathlib import Path
from twisted.python.procutils import which
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.log import getLogger
from .common import async_process


log = getLogger(__name__)





try:
    ffmpeg_path = which('ffmpeg')[0]
except IndexError:
    log.warning(_(
        "ffmpeg executable not found, video thumbnails won't be available"))
    ffmpeg_path = None


async def get_thumbnail(video_path: Union[Path, str], dest_path: Path) -> Path:
    """Extract thumbnail from video

    @param video_path: source of the video
    @param dest_path: path where the file must be saved
    @return: path of the generated thumbnail
        image is created in temporary directory but is not delete automatically
        it should be deleted after use.
        Image will be in JPEG format.
    @raise exceptions.NotFound: ffmpeg is missing
    """
    if ffmpeg_path is None:
        raise exceptions.NotFound(
            _("ffmpeg executable is not available, can't generate video thumbnail"))

    await async_process.run(
        ffmpeg_path, "-i", str(video_path), "-ss", "10", "-frames:v", "1", str(dest_path)
    )
