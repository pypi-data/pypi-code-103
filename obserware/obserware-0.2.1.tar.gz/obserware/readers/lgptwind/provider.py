"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import psutil


def return_mainscreen_threaded_statistics():
    partinfo = [
        indx
        for indx in psutil.disk_partitions(all=True)
        if indx not in psutil.disk_partitions(all=False)
    ]
    partlist, partqant = [], 0
    for indx in partinfo:
        partlist.append(
            (indx.device, indx.mountpoint, indx.fstype, indx.maxfile, indx.maxpath)
        )
        partqant += 1
    retndata = {"partlist": partlist, "partqant": partqant}
    return retndata
