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


class NumPyHyperstack:
    """Provides hyperstack (4D bitmap) and movable single 3D “section” of it.
    """

    def __init__(self, hyperstack):
        self.hyperstack = hyperstack
        self.current_frame = None
        self.t = None
        self.shape = self.hyperstack.shape
        self.frame_count = self.shape[0]
        self.frame_shape = self.shape[1:]

    def select_frame(self, t):
        t = int(t)

        # TODO Pad arrays smaller than 16×256×256 (these arrays are not supported by all OpenGL implementations)
        self.current_frame = \
            np.ascontiguousarray(
                self.hyperstack[t, :]
            )
        self.t = t


class TiffFileVirtualStack(NumPyHyperstack):
    """Hyperstack that is backed by memory-mapped TIFF data.
    """

    def __init__(self, path):
        # TODO Support files with multiple channels
        img = tiff.memmap(path, mode='r')
        print(f'Original shape: {img.shape}')
        if len(img.shape) == 3:
            z, y, x = img.shape
            img = img.reshape([1, z, y, x])

        if len(img.shape) != 4:
            raise TiffFileVirtualStack.UnsupportedFileError(
                'Format of this file is not supported. Make sure it has only single channel and contains volumetric data.')
        t, z, y, x = img.shape
        print(f'Shape after normalization: {img.shape}')

        super().__init__(img)

    class UnsupportedFileError(ValueError):
        pass
