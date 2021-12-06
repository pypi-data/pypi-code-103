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
module to define a standard tomography acquisition (made by bliss)
"""

__authors__ = [
    "H. Payno",
    "J. Garriga",
]
__license__ = "MIT"
__date__ = "19/04/2021"


from nxtomomill.converter.hdf5.acquisition.standardacquisition import (
    StandardAcquisition,
)
import logging

_logger = logging.getLogger(__name__)


class XRD3DAcquisition(StandardAcquisition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_tilt = None
        self._rocking = None

    @property
    def base_tilt(self):
        return self._base_tilt

    @base_tilt.setter
    def base_tilt(self, base_tilt):
        self._base_tilt = base_tilt

    @property
    def rocking(self):
        return self._rocking

    @rocking.setter
    def rocking(self, rocking):
        self._rocking = rocking

    def _get_rocking_dataset(self, entry, n_frames):
        for grp in self._get_positioners_node(entry), entry:
            try:
                rocking, unit = self._get_node_values_for_frame_array(
                    node=grp,
                    n_frame=n_frames,
                    keys=self.configuration.rocking_keys,
                    info_retrieve="rocking",
                    expected_unit=None,
                )
            except (ValueError, KeyError):
                pass
            else:
                return rocking, None

        mess = "Unable to find rocking for {}" "".format(self.root_url.path())
        if self.raise_error_if_issue:
            raise ValueError(mess)
        else:
            mess += "default value will be set. (0)"
            _logger.warning(mess)
            return 0, None

    def _get_base_tilt_dataset(self, entry, n_frames):
        for grp in self._get_positioners_node(entry), entry:
            try:
                base_tilt, unit = self._get_node_values_for_frame_array(
                    node=grp,
                    n_frame=n_frames,
                    keys=self.configuration.base_tilt_keys,
                    info_retrieve="base tilt",
                    expected_unit=None,
                )
            except (ValueError, KeyError):
                pass
            else:
                return base_tilt, None

        mess = "Unable to find base tilt for {}" "".format(self.root_url.path())
        if self.raise_error_if_issue:
            raise ValueError(mess)
        else:
            mess += "default value will be set. (0)"
            _logger.warning(mess)
            return 0, None

    def _treate_valid_camera(
        self,
        detector_node,
        entry,
        frame_type,
        input_file_path,
        output_file,
        entry_path,
        entry_url,
    ):
        super()._treate_valid_camera(
            detector_node=detector_node,
            entry=entry,
            frame_type=frame_type,
            input_file_path=input_file_path,
            output_file=output_file,
            entry_path=entry_path,
            entry_url=entry_url,
        )
        # store base tilt information
        if not self._ignore_sample_output("base_tilt"):
            base_tilt, _ = self._get_base_tilt_dataset(
                entry=entry, n_frames=self._current_scan_n_frame
            )
            self._base_tilt.extend(base_tilt)
        else:
            self._base_tilt = None
        # store rocking information
        if not self._ignore_sample_output("rocking"):
            rocking, _ = self._get_rocking_dataset(
                entry=entry, n_frames=self._current_scan_n_frame
            )
            self._rocking.extend(rocking)
        else:
            self._rocking = None

    def _preprocess_registered_entries(self, output_file):
        self._base_tilt = []
        self._rocking = []
        super()._preprocess_registered_entries(output_file=output_file)

    def _write_sample(self, root_node):
        super()._write_sample(root_node)
        sample_node = root_node.require_group("sample")
        if self._rocking is not None:
            sample_node["rocking"] = self._rocking
        if self._base_tilt is not None:
            sample_node["base_tilt"] = self._base_tilt
