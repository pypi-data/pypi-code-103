# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2020 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""
module to define some converter utils function
"""

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "02/08/2021"


from tomoscan.io import HDF5File
import h5py
from typing import Iterable


def create_nx_data_group(file_path: str, entry_path: str, axis_scale: list):
    """
    Create the 'Nxdata' group at entry level with soft links on the NXDetector
    and NXsample.

    :param file_path:
    :param entry_path:
    :param axis_scale:
    :return:
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path is expected to be a file")
    if not isinstance(entry_path, str):
        raise TypeError("entry_path is expected to be a file")
    if not isinstance(axis_scale, Iterable):
        raise TypeError("axis_scale is expected to be an Iterable")

    with HDF5File(filename=file_path, mode="a") as h5f:
        entry_group = h5f[entry_path]

        nx_data_grp = entry_group.require_group("data")
        # link detector datasets:
        if not entry_path.startswith("/"):
            entry_path = "/" + entry_path
        for dataset in ("data", "image_key", "image_key_control"):
            dataset_path = "/".join((entry_path, "instrument", "detector", dataset))
            nx_data_grp[dataset] = h5py.SoftLink(dataset_path)
        # link rotation angle
        nx_data_grp["rotation_angle"] = h5py.SoftLink(
            "/".join((entry_path, "sample", "rotation_angle"))
        )

        # write NX attributes
        nx_data_grp.attrs["NX_class"] = "NXdata"
        nx_data_grp.attrs["signal"] = "data"
        nx_data_grp.attrs["SILX_style/axis_scale_types"] = axis_scale
        nx_data_grp["data"].attrs["interpretation"] = "image"


def link_nxbeam_to_root(file_path, entry_path):
    """
    Create the 'Nxdata' group at entry level with soft links on the NXDetector
    and NXsample.

    :param file_path:
    :param entry_path:
    :return:
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path is expected to be a file")
    if not isinstance(entry_path, str):
        raise TypeError("entry_path is expected to be a file")

    if not entry_path.startswith("/"):
        entry_path = "/" + entry_path
    with HDF5File(filename=file_path, mode="a") as h5f:
        entry_group = h5f[entry_path]
        entry_group["beam"] = h5py.SoftLink(
            "/".join((entry_path, "instrument", "beam"))
        )
