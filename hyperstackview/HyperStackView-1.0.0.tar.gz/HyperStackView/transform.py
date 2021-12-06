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

_identity = np.eye(4)

"""Some transformation matrices that can be manipulated in object-oriented and functional way. See ``Transform`` docs.
"""


def pad_vec(vec):
    return np.array([
        vec[0],
        vec[1] if len(vec) > 1 else 0,
        vec[2] if len(vec) > 2 else 0,
        vec[3] if len(vec) > 3 else 1,
    ])


def pad_vec_for_scaling(vec):
    vec = np.array(vec).flatten()
    return np.array([
        vec[0],
        vec[1] if len(vec) > 1 else vec[0],
        vec[2] if len(vec) > 2 else (vec[1] if len(vec) > 1 else vec[0]),
        vec[3] if len(vec) > 3 else 1,
    ])


def unit_vector(vec):
    return vec / np.linalg.norm(vec)


class Transform(np.ndarray):
    """Transformation matrix that can be manipulated in object-oriented and functional way.

    These matrices are fully compatible with NumPy environment.

    Constructor of this class is slightly “magic”: when you try to instantiate ``Transform`` with argument ``items`` set
    to 1-dimensional array (vector), the constructor will create instance of ordinary NumPy array. This behavior has two
    purposes. Firstly, it protects programmer from calling ``Transform`` methods on ordinary vectors (they do not expect
    vectors). and it also allows NumPy ``dot`` function return ordinary vector when multiplying ``Transform`` by vector.

    Create new identity transformation matrix::

      mat = identity()

    Apply then some operation (scaling in this case)::

      mat = mat.scale(2)
      # or
      mat = scale(2, mat)

    Apply it to different matrix:

      mat = mat.apply_to(other_mat)
      # or
      mat = Transform.apply_to(mat, other_mat)
      # or
      mat = other_mat.concat(mat)
      # or
      mat = mat @ other_mat
      # or
      mat = numpy.dot(mat, other_mat)
      # etc.

    Apply it to vector:

      mat = mat.apply_to(vector)
      # or any of methods above
    """

    def __new__(cls, items=_identity, dtype=np.float32, **kwargs):
        if len(np.shape(items)) == 1 and len(items) != 16:
            return np.array(items)
        return np.ndarray.__new__(cls, shape=(4, 4), dtype=dtype, buffer=items.astype(dtype), **kwargs)

    def apply_to(self, rhs):
        """Applies this matrix to different matrix.
        """

        if rhs is None:
            return self
        else:
            return np.dot(self, rhs)

    def concat(self, lhs):
        """Applies given matrix to this matrix.
        """

        return lhs.apply_to(self)

    def translate(self, vec):
        return translate(vec, self)

    def scale(self, vec):
        return scale(vec, self)

    def rotate_about(self, axis, angle):
        return rotate_about(axis, angle, self)

    def texture_to_screen(self):
        return self \
            .translate([-.5, -.5, -.5]) \
            .scale(2)

    def screen_to_texture(self):
        return self \
            .scale(.5) \
            .translate([.5, .5, .5])

    def swap_axes(self, a, b):
        return swap_axes(a, b, self)

    def map_z_range(self, from_a, from_b, to_a, to_b):
        return self \
            .translate([0, 0, -from_a]) \
            .scale([1, 1, 1 / (from_b - from_a)]) \
            .scale([1, 1, to_b - to_a]) \
            .translate([0, 0, to_a])

    def drop_axis(self, axis):
        return drop_axis(axis, self)

    def perspective(self, factor):
        return Transform(np.array([
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, factor, 1,
        ])).apply_to(self)


def translate(vec, transform=None):
    t = Transform()
    t[:, 3] = pad_vec(vec)
    return t.apply_to(transform)


def scale(vec, transform=None):
    t = Transform()
    vec = pad_vec_for_scaling(vec)
    t[0, 0] = vec[0]
    t[1, 1] = vec[1]
    t[2, 2] = vec[2]
    t[3, 3] = vec[3]
    return t.apply_to(transform)


def rotate_about(axis, angle, transform=None):
    [l, m, n] = unit_vector(axis)
    c = np.cos(angle)
    s = np.sin(angle)
    c1 = 1 - c

    t = Transform(np.array([
        l * l * c1 + c, m * l * c1 - n * s, n * l * c1 + m * s, 0.0,
        l * m * c1 + n * s, m * m * c1 + c, n * m * c1 - l * s, 0.0,
        l * n * c1 - m * s, m * n * c1 + l * s, n * n * c1 + c, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]))
    return t.apply_to(transform)


def swap_axes(a, b, transform=None):
    t = Transform(np.array([
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 1,
    ]))

    for source_axis in range(0, 3):
        target_axis = source_axis
        if a == source_axis:
            target_axis = b
        elif b == source_axis:
            target_axis = a

        t[target_axis][source_axis] = 1.0

    return t.apply_to(transform)


def drop_axis(axis, transform=None):
    t = Transform()
    t[axis, axis] = 0

    return t.apply_to(transform)


def identity():
    return Transform()
