# -*- coding: utf-8 -*-

# py_tools_ds - A collection of geospatial data analysis tools that simplify standard
# operations when handling geospatial raster and vector data as well as projections.
#
# Copyright (C) 2016-2021
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
# - Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences Potsdam,
#   Germany (https://www.gfz-potsdam.de/)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import numpy as np
import bisect
from typing import Iterable  # noqa F401  # flake8 issue

__author__ = "Daniel Scheffler"


def find_nearest(array, value, roundAlg='auto', extrapolate=False, exclude_val=False, tolerance=0):
    # type: (Iterable, float, str, bool, bool, float) -> float
    """Find the value of an array nearest to a another single value.

    NOTE: In case of extrapolation an EQUALLY INCREMENTED array (like a coordinate grid) is assumed!

    :param array:       array or list of numbers
    :param value:       a number
    :param roundAlg:    <str> 'auto', 'on', 'off'
    :param extrapolate: extrapolate the given array if the given value is outside the array
    :param exclude_val: exclude the given value from possible return values
    :param tolerance:   tolerance (with array = [10, 20, 30] and value=19.9 and roundAlg='off' and tolerance=0.1, 20
                                   is returned)
    """
    assert roundAlg in ['auto', 'on', 'off']
    assert isinstance(array, list) or (isinstance(array, np.ndarray) and len(array.shape) == 1)
    array = sorted(list(array))

    if exclude_val and value in array:
        array.remove(value)

    if extrapolate:
        increment = abs(array[1] - array[0])
        if value > max(array):  # expand array until value
            array = np.arange(min(array), value + 2 * increment, increment)  # 2 * inc to make array_sub work below
        if value < min(array):  # negatively expand array until value
            array = (np.arange(max(array), value - 2 * increment, -increment))[::-1]
    elif value < min(array) or value > max(array):
        raise ValueError('Value %s is outside of the given array.' % value)

    if roundAlg == 'auto':
        diffs = np.abs(np.array(array) - value)
        minDiff = diffs.min()
        minIdx = diffs.argmin()
        isMiddleVal = collections.Counter(diffs)[minDiff] > 1  # value exactly between its both neighbours
        idx = minIdx if not isMiddleVal else bisect.bisect_left(array, value)
        out = array[idx]
    elif roundAlg == 'off':
        idx = bisect.bisect_left(array, value)
        if array[idx] == value:
            out = value  # exact hit
        else:
            idx -= 1
            out = array[idx]  # round off
    else:  # roundAlg == 'on'
        idx = bisect.bisect_left(array, value)
        out = array[idx]

    if tolerance:
        array_sub = array[idx - 1: idx + 2]
        diffs = np.abs(np.array(array_sub) - value)
        inTol = diffs <= tolerance

        if True in inTol:
            out = array_sub[np.argwhere(inTol.astype(int) == 1)[0][0]]

    return out
