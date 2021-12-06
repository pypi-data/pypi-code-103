# HyperStackView -- application for rendering 3D raster images
# Copyright (C) 2021  Jiří Wolker
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import tifffile as tiff

"""This file is simple tool that generates TIFF file of shape 750×750×51 (x×y×z) with three axes and cube placed near
the origin.
"""

img = tiff.memmap('teststack.tif', shape=(51, 750, 750), dtype=np.short, mode='r+')

# Origin cube
for x in range(0, 32):
    for y in range(0, 32):
        for z in range(0, 4):
            img[z, y, x] = 32767

# Striped Z axis
for x in range(8, 16):
    for y in range(8, 16):
        for z in range(0, 51):
            if (z % 8) < 4:
                img[z, y, x] = 32767

# Solid X axis
for x in range(0, 750):
    for y in range(8, 16):
        for z in range(8, 16):
            img[z, y, x] = 32767

# Wavy Y axis
for x in range(8, 16):
    for y in range(0, 750):
        for z in range(8, 16):
            img[z, y, x + y % 64] = 32767

img.flush()
