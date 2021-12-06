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
]
__license__ = "MIT"
__date__ = "27/11/2020"


from .baseacquisition import BaseAcquisition
from .baseacquisition import SourceType
from nxtomomill.io.acquisitionstep import AcquisitionStep
from .baseacquisition import EntryReader
from .baseacquisition import DatasetReader
from .utils import get_entry_type
from .utils import guess_nx_detector
from .utils import get_nx_detectors
from nxtomomill.utils import ImageKey
from nxtomomill.converter.version import version as converter_version
from tomoscan.unitsystem import metricsystem
from tomoscan.io import HDF5File
from silx.io.utils import h5py_read_dataset
import h5py
from silx.io.url import DataUrl
from typing import Union

try:
    import hdf5plugin
except ImportError:
    pass
import logging
import fnmatch
import numpy
import os
from nxtomomill.io.config import TomoHDF5Config
from nxtomomill.converter.utils import create_nx_data_group
from nxtomomill.converter.utils import link_nxbeam_to_root


_logger = logging.getLogger(__name__)


class StandardAcquisition(BaseAcquisition):
    """
    A standard acquisition where all registered scan are connected to
    group an NXTomo entry

    :param DataUrl root_url: url of the acquisition. Can be None if
                             this is the initialization entry
    """

    def __init__(
        self,
        root_url: Union[DataUrl, None],
        configuration: TomoHDF5Config,
        detector_sel_callback,
    ):
        super().__init__(
            root_url=root_url,
            configuration=configuration,
            detector_sel_callback=detector_sel_callback,
        )
        # variables set by the `_preprocess_frames` function
        self._data = None
        """frames as a virtual dataset"""
        self._image_key = None
        """list of image keys"""
        self._image_key_control = None
        """list of image keys"""
        self._rotation_angle = None
        """list of rotation angles"""
        self._x_translation = None
        """x_translation"""
        self._y_translation = None
        """y_translation"""
        self._z_translation = None
        """z_translation"""
        self._n_frames = None
        self._dim_1 = None
        self._dim_2 = None
        self._data_type = None
        self._virtual_sources = None
        self._acq_expo_time = None
        self._copied_dataset = {}
        "register dataset copied. Key if the original location as" "DataUrl.path. Value is the DataUrl it has been moved to"
        self._current_scan_n_frame = None

    @property
    def image_key(self):
        return self._image_key

    @property
    def image_key_control(self):
        return self._image_key_control

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @property
    def x_translation(self):
        return self._x_translation

    @property
    def y_translation(self):
        return self._y_translation

    @property
    def z_translation(self):
        return self._z_translation

    @property
    def n_frames(self):
        return self._n_frames

    @property
    def dim_1(self):
        return self._dim_1

    @property
    def dim_2(self):
        return self._dim_2

    @property
    def data_type(self):
        return self._data_type

    @property
    def expo_time(self):
        return self._acq_expo_time

    @property
    def is_xrd_ct(self):
        return False

    @property
    def require_x_translation(self):
        return True

    @property
    def require_y_translation(self):
        return True

    @property
    def require_z_translation(self):
        return True

    @property
    def has_diode(self):
        return False

    def is_different_sequence(self, entry):
        return True

    def register_step(self, url: DataUrl, entry_type=None, copy_frames=False) -> None:
        """

        :param DataUrl url: entry to be registered and contained in the
                                 acquisition
        :param entry_type: type of the entry if know. Overwise will be
                           'evaluated'
        """
        if entry_type is None:
            entry_type = get_entry_type(url=url, configuration=self.configuration)
        assert (
            entry_type is not AcquisitionStep.INITIALIZATION
        ), "Initialization are root node of a new sequence and not a scan of a sequence"

        if entry_type is None:
            _logger.warning("{} not recognized, skip it".format(url))
        else:
            self._registered_entries[url.path()] = entry_type
            self._copy_frames[url.path()] = copy_frames
            self._entries_o_path[url.path()] = url.data_path()
            # path from the original file. Haven't found another way to get it ?!

    def _get_valid_camera_names(self, instrument_grp: h5py.Group):
        # step one: try to get detector from nx property
        detectors = get_nx_detectors(instrument_grp)
        detectors = [grp.name.split("/")[-1] for grp in detectors]

        def filter_detectors(det_grps):
            if len(det_grps) > 0:
                _logger.info(
                    "{} detector found from NX_class attribute".format(len(det_grps))
                )
                if len(det_grps) > 1:
                    # if an option: pick the first one once orderered
                    # else ask user
                    if self._detector_sel_callback is None:
                        sel_det = det_grps[0]
                        _logger.warning(
                            "several detector found. Only one"
                            "is managed for now. Will pick {}"
                            "".format(sel_det)
                        )
                    else:
                        sel_det = self._detector_sel_callback(det_grps)
                        if sel_det is None:
                            _logger.warning("no detector given, avoid conversion")
                    det_grps = (sel_det,)
                return det_grps
            return None

        detectors = filter_detectors(det_grps=detectors)
        if detectors is not None:
            return detectors

        # step tow: get nx detector from shape...
        detectors = guess_nx_detector(instrument_grp)
        detectors = [grp.name.split("/")[-1] for grp in detectors]
        return filter_detectors(det_grps=detectors)

    def __get_data_from_camera(
        self,
        data_dataset: h5py.Dataset,
        data_name,
        frame_type,
        output_file,
        entry,
        entry_path,
        camera_dataset_url,
    ):
        if data_dataset.ndim == 2:
            shape = (1, data_dataset.shape[0], data_dataset.shape[1])
        elif data_dataset.ndim != 3:
            err = "dataset %s is expected to be 3D when %sD found." % (
                data_name,
                data_dataset.ndim,
            )
            if data_dataset.ndim == 1:
                err = "\n".join(
                    err,
                    "This might be a bliss-EDF dataset. Those are not handled by nxtomomill",
                )
            raise ValueError(err)
        else:
            shape = data_dataset.shape

        n_frame = shape[0]
        self._n_frames += n_frame
        if self.dim_1 is None:
            self._dim_2 = shape[1]
            self._dim_1 = shape[2]
        else:
            if self._dim_1 != shape[2] or self._dim_2 != shape[1]:
                raise ValueError("Inconsistency in detector shapes")
        if self._data_type is None:
            self._data_type = data_dataset.dtype
        elif self._data_type != data_dataset.dtype:
            raise ValueError("detector frames have incoherent " "data types")

        # update image_key and image_key_control
        # Note: for now there is no image_key on the master file
        # should be added later.
        image_key_control = frame_type.to_image_key_control()
        image_key = frame_type.to_image_key()
        self._image_key_control.extend([image_key_control.value] * n_frame)
        self._image_key.extend([image_key.value] * n_frame)
        # create virtual source (getting ready for writing)
        rel_input = os.path.relpath(
            camera_dataset_url.file_path(), os.path.dirname(output_file)
        )
        data_dataset_path = data_dataset.name.replace(entry.name, entry_path, 1)
        # replace data_dataset name by the original entry_path.
        # this is a workaround to use the dataset path on the
        # "treated file". Because .name if the name on the 'target'
        # file of the virtual dataset
        v_source = h5py.VirtualSource(rel_input, data_dataset_path, data_dataset.shape)
        self._virtual_sources.append(v_source)
        self._virtual_sources_len.append(n_frame)
        return n_frame

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
        if "data_cast" in detector_node:
            _logger.warning(
                "!!! looks like this data has been cast. Take cast data for %s!!!"
                % detector_node
            )
            data_dataset = detector_node["data_cast"]
            data_name = "/".join((detector_node.name, "data_cast"))
        else:
            data_dataset = detector_node["data"]
            data_name = "/".join((detector_node.name, "data"))

        camera_dataset_url = DataUrl(
            file_path=entry_url.file_path(), data_path=data_name, scheme="silx"
        )

        if self._copy_frames[entry_url.path()]:
            from nxtomomill.utils import embed_url

            created_url = embed_url(
                url=camera_dataset_url,
                output_file=output_file,
            )
            self._copied_dataset[camera_dataset_url.path()] = created_url
            with DatasetReader(created_url) as copied_data_dataset:
                n_frame = self.__get_data_from_camera(
                    copied_data_dataset,
                    data_name=data_name,
                    frame_type=frame_type,
                    output_file=output_file,
                    entry=entry,
                    entry_path=created_url.data_path(),
                    camera_dataset_url=created_url,
                )
        else:
            n_frame = self.__get_data_from_camera(
                data_dataset,
                data_name=data_name,
                frame_type=frame_type,
                output_file=output_file,
                entry=entry,
                entry_path=entry_path,
                camera_dataset_url=camera_dataset_url,
            )

        # store rotation
        if not self._ignore_sample_output("rotation_angle"):
            rots = self._get_rotation_angle(root_node=entry, n_frame=n_frame)[0]
            self._rotation_angle.extend(rots)
        else:
            self._rotation_angle = None

        if self.require_x_translation and not self._ignore_sample_output(
            "x_translation"
        ):
            self._x_translation.extend(
                self._get_x_translation(root_node=entry, n_frame=n_frame)[0]
            )
        else:
            self._x_translation = None

        if self.require_y_translation and not self._ignore_sample_output(
            "y_translation"
        ):
            self._y_translation.extend(
                self._get_y_translation(root_node=entry, n_frame=n_frame)[0]
            )
        else:
            self._y_translation = None

        if self.require_z_translation and not self._ignore_sample_output(
            "z_translation"
        ):
            self._z_translation.extend(
                self._get_z_translation(root_node=entry, n_frame=n_frame)[0]
            )
        else:
            self._z_translation = None

        # store acquisition time
        self._acq_expo_time.extend(
            self._get_expo_time(
                root_node=entry,
                detector_node=detector_node,
                n_frame=n_frame,
            )[0]
        )
        # retrieve data requested by plugins
        for resource_name in self._plugins_pos_resources:
            assert isinstance(resource_name, str), "resource_name should be a string"
            self._plugins_pos_resources[resource_name].extend(
                self._get_plugin_pos_resource(
                    root_node=entry,
                    resource_name=resource_name,
                    n_frame=None,
                )
            )
        for resource_name in self._plugins_instr_resources:
            assert isinstance(resource_name, str), "resource_name should be a string"
            self._plugins_instr_resources[resource_name].extend(
                self._get_plugin_instr_resource(
                    root_node=entry,
                    resource_name=resource_name,
                    n_frame=None,
                )
            )
        self._current_scan_n_frame = n_frame

    def camera_is_valid(self, det_name):
        assert isinstance(det_name, str)
        for vcm in self.configuration.valid_camera_names:
            if fnmatch.fnmatch(det_name, vcm):
                return True
        return False

    def _preprocess_registered_entry(self, entry_url, type_, output_file):
        with EntryReader(entry_url) as entry:
            entry_path = self._entries_o_path[entry_url.path()]
            input_file_path = entry_url.file_path()
            input_file_path = os.path.abspath(
                os.path.relpath(input_file_path, os.getcwd())
            )
            input_file_path = os.path.realpath(input_file_path)
            if type_ is AcquisitionStep.INITIALIZATION:
                raise RuntimeError(
                    "no initialization should be registered."
                    "There should be only one per acquisition."
                )

            if "instrument" not in entry:
                _logger.error(
                    "no instrument group found in %s, unable to"
                    "retrieve frames" % entry.name
                )
                return

            # if we need to guess detector name(s)
            instrument_grp = entry["instrument"]
            if self.configuration.valid_camera_names is None:
                det_grps = self._get_valid_camera_names(instrument_grp)
                # update valid camera names
                self.configuration.valid_camera_names = det_grps

            for key, det_grp in instrument_grp.items():
                if (
                    "NX_class" in instrument_grp[key].attrs
                    and instrument_grp[key].attrs["NX_class"] == "NXdetector"
                ):
                    _logger.debug(
                        "Found one detector at %s for %s." % (key, entry.name)
                    )

                    # diode
                    if self.has_diode:
                        try:
                            diode_vals, diode_unit = self._get_diode(
                                root_node=entry, n_frame=self.n_frames
                            )
                        except Exception:
                            pass
                        else:
                            self._diode.extend(diode_vals)

                    if not self.camera_is_valid(key):
                        _logger.debug(f"ignore {key}, not a `valid` camera name")
                        continue
                    else:
                        detector_node = instrument_grp[key]
                        _logger.info(f"start treatment of detector {detector_node}")
                        self._treate_valid_camera(
                            detector_node,
                            entry=entry,
                            frame_type=type_,
                            input_file_path=input_file_path,
                            output_file=output_file,
                            entry_path=entry_path,
                            entry_url=entry_url,
                        )

    def _preprocess_registered_entries(self, output_file):
        """parse all frames of the different steps and retrieve data,
        image_key..."""
        self._n_frames = 0
        self._dim_1 = None
        self._dim_2 = None
        self._data_type = None
        self._x_translation = []
        self._y_translation = []
        self._z_translation = []
        self._image_key = []
        self._image_key_control = []
        self._rotation_angle = []
        self._virtual_sources = []
        self._virtual_sources_len = []
        self._diode = []
        self._acq_expo_time = []
        self._diode_unit = None
        self._copied_dataset = {}

        # if rotation motor is not defined try to deduce it from root_url/technique/scan/motor
        if self.configuration.rotation_angle_keys is None:
            rotation_motor = self._read_rotation_motor_name()
            if rotation_motor is not None:
                self.configuration.rotation_angle_keys = (rotation_motor,)
            else:
                self.configuration.rotation_angle_keys = tuple()

        # list of data virtual source for the virtual dataset
        for entry_url, type_ in self._registered_entries.items():
            url = DataUrl(path=entry_url)
            self._preprocess_registered_entry(url, type_, output_file=output_file)

        if len(self._diode) == 0:
            self._diode = None
        if self._diode is not None:
            self._diode = numpy.asarray(self._diode)
            self._diode = self._diode / self._diode.mean()
        for plugin in self._plugins:
            plugin.set_positioners_infos(self._plugins_pos_resources)
            plugin.set_instrument_infos(self._plugins_instr_resources)

    def _get_diode(self, root_node, n_frame) -> tuple:
        values, unit = self._get_node_values_for_frame_array(
            node=root_node["measurement"],
            n_frame=n_frame,
            keys=self.configuration.diode_keys,
            info_retrieve="diode",
            expected_unit="volt",
        )
        return values, unit

    def get_already_defined_params(self, key):
        defined = self.__get_extra_param(key=key)
        if len(defined) > 1:
            raise ValueError("{} are aliases. Only one should be defined")
        elif len(defined) == 0:
            return None
        else:
            return list(defined.values())[0]

    def __get_extra_param(self, key) -> dict:
        """return already defined parameters for one key.
        A key as aliases so it returns a dict"""
        aliases = list(TomoHDF5Config.EXTRA_PARAMS_ALIASES[key])
        aliases.append(key)
        res = {}
        for alias in aliases:
            if alias in self.configuration.param_already_defined:
                res[alias] = self.configuration.param_already_defined[alias]
        return res

    def _write_beam(self, root_node, request_input, input_callback):
        instrument_node = root_node.require_group("instrument")
        beam_node = instrument_node.require_group("beam")

        already_defined = self.get_already_defined_params(
            key=TomoHDF5Config.EXTRA_PARAMS_ENERGY_DK
        )
        if already_defined is not None:
            energy = float(already_defined)
            unit = "kev"
        else:
            energy, unit = self._get_energy(
                ask_if_0=request_input, input_callback=input_callback
            )
        if energy is not None:
            beam_node["incident_energy"] = energy
            beam_node["incident_energy"].attrs["unit"] = unit

        if "NX_class" not in beam_node.attrs:
            beam_node.attrs["NX_class"] = "NXbeam"

    def _write_instrument(self, root_node):
        # handle instrument
        instrument_node = root_node.require_group("instrument")
        instrument_node.attrs["NX_class"] = "NXinstrument"
        instrument_title = self._get_instrument_name()
        if instrument_title:
            instrument_node["name"] = instrument_title

        detector_node = instrument_node.require_group("detector")
        detector_node.attrs["NX_class"] = "NXdetector"
        # write data
        if self._virtual_sources is not None:
            self._create_data_virtual_dataset(detector_node)
        if self.image_key is not None:
            detector_node["image_key"] = self.image_key
        if self.image_key_control is not None:
            detector_node["image_key_control"] = self.image_key_control
        if self._acq_expo_time is not None:
            detector_node["count_time"] = self._acq_expo_time
            detector_node["count_time"].attrs["unit"] = "s"
        # write distance
        already_defined = self.get_already_defined_params(
            key=TomoHDF5Config.EXTRA_PARAMS_DISTANCE
        )
        if already_defined is not None:
            distance = float(already_defined)
            unit = "m"
        else:
            distance, unit = self._get_distance()
        if distance is not None:
            detector_node["distance"] = distance
            detector_node["distance"].attrs["unit"] = unit
        # write x and y pixel size
        # if magnified pixel size is found then we right this value.
        # otherwise will take pixel size (if found)
        already_defined = self.get_already_defined_params(
            key=TomoHDF5Config.EXTRA_PARAMS_X_PIXEL_SIZE_DK
        )
        if already_defined is not None:
            x_pixel_size = float(already_defined)
            unit = "m"
        else:
            x_pixel_size, unit = self._get_pixel_size("x")
        if x_pixel_size is not None:
            detector_node["x_pixel_size"] = x_pixel_size
            detector_node["x_pixel_size"].attrs["unit"] = unit

        already_defined = self.get_already_defined_params(
            key=TomoHDF5Config.EXTRA_PARAMS_Y_PIXEL_SIZE_DK
        )
        if already_defined is not None:
            y_pixel_size = float(already_defined)
            unit = "m"
        else:
            y_pixel_size, unit = self._get_pixel_size("y")
        if y_pixel_size is not None:
            detector_node["y_pixel_size"] = y_pixel_size
            detector_node["y_pixel_size"].attrs["unit"] = unit
        # write field of view
        fov = self._get_field_of_fiew()
        if fov is not None:
            detector_node["field_of_view"] = fov
            if fov.lower() == "half":
                estimated_cor, unit = self._get_estimated_cor_from_motor(
                    pixel_size=y_pixel_size
                )
                if estimated_cor is not None:
                    detector_node["estimated_cor_from_motor"] = estimated_cor
                    detector_node["estimated_cor_from_motor"].attrs["unit"] = unit
        # write tomo_n
        tomo_n = self._get_tomo_n()
        if tomo_n is not None:
            # save tomo n
            detector_node["tomo_n"] = tomo_n
        # write nx_source
        source_grp = instrument_node.require_group("source")
        source_name = self._get_source_name()
        if source_name:
            source_grp["name"] = source_name
        source_type = self._get_source_type()
        if source_type:
            # as the value is not saved as a standard value at esrf adapt the value to a standard one
            if "synchrotron" in source_type.lower():
                source_type = SourceType.SYNCHROTRON_X_RAY_SOURCE.value
            # drop a warning if the source type is invalid
            if source_type not in SourceType.values():
                _logger.warning(
                    "Source type ({}) is not a 'standard value'".format(source_type)
                )
            source_grp["type"] = source_type

        if "NX_class" not in source_grp.attrs:
            source_grp.attrs["NX_class"] = "NXsource"

    def _create_data_virtual_dataset(self, detector_node):
        if (
            self.n_frames is None
            or self.dim_1 is None
            or self.dim_2 is None
            or self.data_type is None
        ):
            if self.n_frames is None:
                _logger.error("unable to get the number of frames")
            if self.dim_1 is None:
                _logger.error("unable to get frame dim_1")
            if self.dim_2 is None:
                _logger.error("unable to get frame dim_2")
            if self.data_type is None:
                _logger.error("unable to get data type")
            raise ValueError(
                "Preprocessing could not deduce all information "
                "for creating the `data` virtual dataset"
            )
        layout = h5py.VirtualLayout(
            shape=(self.n_frames, self.dim_2, self.dim_1), dtype=self.data_type
        )
        last = 0
        for v_source, vs_len in zip(self._virtual_sources, self._virtual_sources_len):
            layout[last : vs_len + last] = v_source
            last += vs_len

        detector_node.create_virtual_dataset("data", layout)
        detector_node["data"].attrs["NX_class"] = "NXdata"
        detector_node["data"].attrs[
            "SILX_style/axis_scale_types"
        ] = self.get_axis_scale_types()
        detector_node["data"].attrs["interpretation"] = "image"

    def _check_has_metadata(self):
        if self.root_url is None:
            raise ValueError(
                "no initialization entry specify, unable to" "retrieve energy"
            )

    def _write_sample(self, root_node):
        sample_node = root_node.create_group("sample")
        sample_node.attrs["NX_class"] = "NXsample"
        sample_name = self._get_sample_name()
        if sample_name:
            sample_node["name"] = sample_name
        group_size = self._get_grp_size()
        if group_size:
            sample_node.attrs["group_size"] = group_size
        if self.rotation_angle is not None:
            sample_node["rotation_angle"] = self.rotation_angle
            sample_node["rotation_angle"].attrs["unit"] = "degree"
        if self.require_x_translation and self.x_translation is not None:
            sample_node["x_translation"] = self.x_translation
            sample_node["x_translation"].attrs["unit"] = "m"
        if self.require_y_translation and self.y_translation is not None:
            sample_node["y_translation"] = self.y_translation
            sample_node["y_translation"].attrs["unit"] = "m"
        if self.require_z_translation and self.z_translation is not None:
            sample_node["z_translation"] = self.z_translation
            sample_node["z_translation"].attrs["unit"] = "m"

    def _write_diode(self, root_node):
        assert self.has_diode, "this acquisition does not expect diode"
        diode_node = root_node.create_group("diode")
        diode_node.attrs["NX_class"] = "NXdetector"
        diode_node["data"] = self._diode
        if self._diode_unit is not None:
            diode_node["data"].attrs["unit"] = self._diode_unit

    def _write_plugins_output(self, root_node):
        for plugin in self._plugins:
            instrument_node = root_node["instrument"]
            detector_node = instrument_node["detector"]
            detector_node.attrs["NX_class"] = "NXdetector"
            plugin.write(
                root_node=root_node,
                sample_node=root_node["sample"],
                detector_node=detector_node,
                beam_node=root_node["instrument/beam"],
            )

    def _generic_path_getter(self, path, message, level="warning"):
        """
        :param str level: level can be logging.level values : "warning", "error", "info"
        """
        if self.root_url is None:
            return None
        self._check_has_metadata()
        with self.read_entry() as entry:
            if path in entry:
                return h5py_read_dataset(entry[path])
            else:
                if message is not None:
                    getattr(_logger, level)(message)
                return None

    def _get_source_name(self):
        """ """
        return self._generic_path_getter(
            path=self._SOURCE_NAME, message="Unable to find source name", level="info"
        )

    def _get_source_type(self):
        """ """
        return self._generic_path_getter(
            path=self._SOURCE_TYPE, message="Unable to find source type", level="info"
        )

    def _get_title(self):
        """return acquisition title"""
        return self._generic_path_getter(
            path=self._TITLE_PATH, message="Unable to find title"
        )

    def _get_instrument_name(self):
        """:return instrument title / name"""
        return self._generic_path_getter(
            path=self._INSTRUMENT_NAME_PATH,
            message="Unable to find instrument name",
            level="info",
        )

    def _get_dataset_name(self):
        """return name of the acquisition"""
        return self._generic_path_getter(
            path=self._DATASET_NAME_PATH,
            message="No name describing the acquisition has been "
            "found, Name dataset will be skip",
        )

    def _get_sample_name(self):
        """return sample name"""
        return self._generic_path_getter(
            path=self._SAMPLE_NAME_PATH,
            message="No sample name has been "
            "found, Sample name dataset will be skip",
        )

    def _get_grp_size(self):
        """return the nb_scans composing the zseries if is part of a group
        of sequence"""
        return self._generic_path_getter(
            path=self._GRP_SIZE_PATH,
            message=None,
        )

    def _get_tomo_n(self):
        return self._generic_path_getter(
            path=self._TOMO_N_PATH,
            message="unable to find information regarding tomo_n",
        )

    def _get_start_time(self):
        return self._generic_path_getter(
            path=self._START_TIME_PATH,
            message="Unable to find start time",
            level="info",
        )

    def _get_end_time(self):
        return self._generic_path_getter(
            path=self._END_TIME_PATH, message="Unable to find end time", level="info"
        )

    def _get_energy(self, ask_if_0, input_callback):
        """return tuple(energy, unit)"""
        if self.root_url is None:
            return None, None
        self._check_has_metadata()
        with self.read_entry() as entry:
            if self._ENERGY_PATH in entry:
                energy = h5py_read_dataset(entry[self._ENERGY_PATH])
                unit = self._get_unit(entry[self._ENERGY_PATH], default_unit="kev")
                if energy == 0 and ask_if_0:
                    desc = (
                        "Energy has not been registered. Please enter "
                        "incoming beam energy (in kev):"
                    )
                    if input_callback is None:
                        en = input(desc)
                    else:
                        en = input_callback("energy", desc)
                    if energy is not None:
                        energy = float(en)
                return energy, unit
            else:
                mess = "unable to find energy for entry {}.".format(entry)
                if self.raise_error_if_issue:
                    raise ValueError(mess)
                else:
                    mess += " Default value will be set (19kev)"
                    _logger.warning(mess)
                    return 19.0, "kev"

    def _get_distance(self):
        """return tuple(distance, unit)"""
        if self.root_url is None:
            return None, None
        self._check_has_metadata()
        with self.read_entry() as entry:
            for key in self.configuration.sample_detector_distance_paths:
                if key in entry:
                    node = entry[key]
                    distance = h5py_read_dataset(node)
                    unit = self._get_unit(node, default_unit="cm")
                    # convert to meter
                    distance = (
                        distance * metricsystem.MetricSystem.from_value(unit).value
                    )
                    return distance, "m"
            mess = "unable to find distance for entry {}.".format(entry)
            if self.raise_error_if_issue:
                raise ValueError(mess)
            else:
                mess += "Default value will be set (1m)"
                _logger.warning(mess)
                return 1.0, "m"

    def _get_pixel_size(self, axis):
        """return tuple(pixel_size, unit)"""
        if self.root_url is None:
            return None, None
        assert axis in ("x", "y")
        self._check_has_metadata()
        keys = (
            self.configuration.x_pixel_size_paths
            if axis == "x"
            else self.configuration.y_pixel_size_paths
        )
        with self.read_entry() as entry:
            for key in keys:
                if key in entry:
                    node = entry[key]
                    node_item = h5py_read_dataset(node)
                    # if the pixel size is provided as x, y
                    if isinstance(node_item, numpy.ndarray):
                        if len(node_item) > 1 and axis == "y":
                            size_ = node_item[1]
                        else:
                            size_ = node_item[0]
                    # if this is a single value
                    else:
                        size_ = node_item
                    unit = self._get_unit(node, default_unit="micrometer")
                    # convert to meter
                    size_ = size_ * metricsystem.MetricSystem.from_value(unit).value
                    return size_, "m"

            mess = "unable to find {} pixel size for entry {}".format(axis, entry)
            if self.raise_error_if_issue:
                raise ValueError(mess)
            else:
                mess += "default value will be set to 10-6m"
                _logger.warning(mess)
                return 10e-6, "m"

    def _get_field_of_fiew(self):
        if self.configuration.field_of_view is not None:
            return self.configuration.field_of_view.value
        if self.root_url is None:
            return None
        with self.read_entry() as entry:
            if self._FOV_PATH in entry:
                return h5py_read_dataset(entry[self._FOV_PATH])
            else:
                mess = (
                    "unable to find information regarding field of view for"
                    " entry {}".format(entry)
                )
                # FOV is optional: shouldn't won't raise an error
                mess += "set it to default value (Full)"
                _logger.warning(mess)
                return "Full"

    def _get_estimated_cor_from_motor(self, pixel_size):
        """given pixel is expected to be given in meter"""
        if self.root_url is None:
            return None, None
        with self.read_entry() as entry:
            if self.configuration.y_rot_key in entry:
                y_rot = h5py_read_dataset(entry[self.configuration.y_rot_key])
            else:
                _logger.warning(
                    "unable to find information on positioner {}".format(
                        self.configuration.y_rot_key
                    )
                )
                return None, None
            # y_rot is provided in mm when pixel size is in meter.
            y_rot = y_rot * metricsystem.millimeter.value

            if pixel_size is None:
                mess = (
                    "pixel size is required to estimate the cor from the "
                    "motor position on pixels"
                )
                if self.raise_error_if_issue:
                    raise ValueError(mess)
                else:
                    mess += " Set default value (0m)"
                    _logger.warning(mess)
                    return 0, "m"
            else:
                return y_rot / pixel_size, "pixels"

    def write_as_nxtomo(
        self,
        output_file: str,
        data_path: str,
        input_file_path: str,
        request_input: bool,
        plugins,
        input_callback=None,
    ) -> None:
        """
        write the current sequence in an NXtomo like

        :param str output_file: destination file
        :param str data_path: path to store the data in the destination file
        :param str input_file_path: hdf5 source file
        :param bool request_input: if some entries are missing should we ask
                                   the user for input
        :param list plugins: plugins to process
        :param input_callback: if provided then will call this callback
                               function with  (missing_entry, desc) instead of
                               input
        """
        _logger.info(
            "write data of {} to {}".format(self, output_file + "::/" + data_path)
        )
        self.set_plugins(plugins)

        # work on absolute path. The conversion to relative path and
        # then to absolute path is a trick in case there is some 'mounted'
        # directory exposed differently.
        # Like '/mnt/multipath-shares/tmp_14_days'
        output_file = os.path.abspath(os.path.relpath(output_file, os.getcwd()))
        output_file = os.path.realpath(output_file)

        # first retrieve the data and create some virtual dataset.
        self._preprocess_registered_entries(output_file=output_file)
        with HDF5File(output_file, "a") as h5_file:
            entry = h5_file.require_group(data_path)
            entry.attrs["NX_class"] = "NXentry"
            entry.attrs["definition"] = "NXtomo"
            entry.attrs["version"] = converter_version()
            entry.attrs["default"] = "data"
            start_time = self._get_start_time()
            if start_time is not None:
                entry["start_time"] = start_time
            end_time = self._get_end_time()
            if end_time is not None:
                entry["end_time"] = end_time
            dataset_name = self._get_dataset_name()
            if dataset_name:
                entry["title"] = dataset_name
            entry["definition"] = "NXtomo"

            self._write_beam(
                entry, request_input=request_input, input_callback=input_callback
            )
            self._write_instrument(entry)
            self._write_sample(entry)
            self._write_plugins_output(entry)
            if self.has_diode:
                self._write_diode(entry)

        # create nxdata group
        try:
            create_nx_data_group(
                file_path=output_file,
                entry_path=data_path,
                axis_scale=self.get_axis_scale_types(),
            )
        except Exception as e:
            if self.raise_error_if_issue:
                raise e
            else:
                _logger.error(
                    "Fail to create NXdata group. Reason is {}".format(str(e))
                )

        # create beam group at root for compatibility
        link_nxbeam_to_root(file_path=output_file, entry_path=data_path)

        # check scan is complete
        tomo_n = self._get_tomo_n()
        if tomo_n is not None:
            image_key_control = numpy.asarray(self._image_key_control)
            proj_found = len(
                image_key_control[image_key_control == ImageKey.PROJECTION.value]
            )
            if proj_found < tomo_n:
                mess = (
                    "Incomplete scan. Expect {} projection "
                    "but only {} found".format(tomo_n, proj_found)
                )
                if self.configuration.raises_error is True:
                    raise ValueError(mess)
                else:
                    _logger.error(mess)
