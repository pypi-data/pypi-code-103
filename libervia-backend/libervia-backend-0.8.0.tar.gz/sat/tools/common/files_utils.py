#!/usr/bin/env python3

# SaT: an XMPP client
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

"""tools to help manipulating files"""
from pathlib import Path


def get_unique_name(path):
    """Generate a path with a name not conflicting with existing file

    @param path(str, Path): path to the file to create
    @return (Path): unique path (can be the same as path if there is no conflict)
    """
    ori_path = path = Path(path)
    idx = 1
    while path.exists():
        path = ori_path.with_name(f"{ori_path.stem}_{idx}{ori_path.suffix}")
        idx += 1
    return path
