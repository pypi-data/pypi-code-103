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


import getpass
from os import uname

import cpuinfo
import psutil


def return_bottombar_threaded_statistics():
    retndata = {
        "cpud_percent": psutil.cpu_percent(),
        "memo_percent": psutil.virtual_memory().percent,
        "swap_percent": psutil.swap_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
    return retndata


def return_bottombar_onetimed_statistics():
    retndata = {
        "username": getpass.getuser(),
        "hostname": uname().nodename,
        "systname": uname().sysname,
        "rlsename": uname().release,
    }
    return retndata


def return_mainscreen_threaded_statistics():
    retndata = {
        "memo": {
            "percentage": {
                "used": psutil.virtual_memory().used
                * 100
                / psutil.virtual_memory().total,
                "cached": psutil.virtual_memory().cached
                * 100
                / psutil.virtual_memory().total,
                "free": psutil.virtual_memory().free
                * 100
                / psutil.virtual_memory().total,
            },
            "absolute": {
                "used": psutil.virtual_memory().used // 1048576,
                "cached": psutil.virtual_memory().cached // 1048576,
                "free": psutil.virtual_memory().free // 1048576,
                "total": psutil.virtual_memory().total // 1048576,
                "active": psutil.virtual_memory().active // 1048576,
                "buffers": psutil.virtual_memory().buffers // 1048576,
                "shared": psutil.virtual_memory().shared // 1048576,
                "slab": psutil.virtual_memory().slab // 1048576,
            },
        },
        "swap": {
            "percentage": {
                "used": psutil.swap_memory().used * 100 / psutil.swap_memory().total,
                "free": psutil.swap_memory().free * 100 / psutil.swap_memory().total,
            },
            "absolute": {
                "used": psutil.swap_memory().used // 1048576,
                "free": psutil.swap_memory().free // 1048576,
                "total": psutil.swap_memory().total // 1048576,
                "sin": psutil.swap_memory().sin // 1048576,
                "sout": psutil.swap_memory().sout // 1048576,
            },
        },
        "cpud": {
            "percentage": {
                "used": psutil.cpu_percent(),
                "free": 100 - psutil.cpu_percent(),
            },
            "absolute": {
                "ctx_switches": psutil.cpu_stats().ctx_switches,
                "interrupts": psutil.cpu_stats().interrupts,
                "soft_interrupts": psutil.cpu_stats().soft_interrupts,
                "sys_calls": psutil.cpu_stats().syscalls,
            },
        },
    }
    return retndata
