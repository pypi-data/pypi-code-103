# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2019 European Synchrotron Radiation Facility
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
"""An :class:`.Enum` class with additional features."""

from __future__ import absolute_import

__authors__ = ["T. Vincent", "H. Payno"]
__license__ = "MIT"
__date__ = "29/04/2019"


import enum
import sys
import typing
import numpy
import os
import contextlib
from tomoscan.io import HDF5File
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from silx.io.url import DataUrl
from silx.io.utils import get_data
import logging
import h5py
from silx.utils.deprecation import deprecated

try:
    import hdf5plugin
except ImportError:
    pass
from collections.abc import Iterable
from silx.utils.enum import Enum as _Enum
import uuid
from silx.io.utils import h5py_read_dataset
import h5py._hl.selections as selection
from h5py import h5s as h5py_h5s


class ImageKey(_Enum):
    """
    Possible values of image_key_control
    """

    ALIGNMENT = -1
    PROJECTION = 0
    FLAT_FIELD = 1
    DARK_FIELD = 2
    INVALID = 3


class FieldOfView(_Enum):
    FULL = "Full"
    HALF = "Half"


@contextlib.contextmanager
def cwd_context():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


class Enum(enum.Enum):
    """Enum with additional class methods."""

    @classmethod
    def from_value(cls, value):
        """Convert a value to corresponding Enum member

        :param value: The value to compare to Enum members
           If it is already a member of Enum, it is returned directly.
        :return: The corresponding enum member
        :rtype: Enum
        :raise ValueError: In case the conversion is not possible
        """
        if isinstance(value, cls):
            return value
        for member in cls:
            if value == member.value:
                return member
        raise ValueError("Cannot convert: %s" % value)

    @classmethod
    def members(cls):
        """Returns a tuple of all members.

        :rtype: Tuple[Enum]
        """
        return tuple(member for member in cls)

    @classmethod
    def names(cls):
        """Returns a tuple of all member names.

        :rtype: Tuple[str]
        """
        return tuple(member.name for member in cls)

    @classmethod
    def values(cls):
        """Returns a tuple of all member values.

        :rtype: Tuple
        """
        return tuple(member.value for member in cls)


def embed_url(url: DataUrl, output_file: str) -> DataUrl:
    """
    Create a dataset under duplicate_data and with a random name
    to store it

    :param DataUrl url: dataset to be copied
    :param str output_file: where to store the dataset
    :param expected_type: some metadata to put in copied dataset attributes
    :type expected_type: Union[None, AcquisitionStep]
    :param data: data loaded from url is already loaded
    :type data: None, numpy.array
    """
    if not isinstance(url, DataUrl):
        return url
    elif url.file_path() == output_file:
        return url
    else:
        embed_data_path = "/".join(("/duplicate_data", str(uuid.uuid1())))
        with cwd_context():
            os.chdir(os.path.dirname(os.path.abspath(output_file)))
            with HDF5File(output_file, "a") as h5s:
                h5s[embed_data_path] = get_data(url)
                h5s[embed_data_path].attrs["original_url"] = url.path()
            return DataUrl(
                file_path=output_file, data_path=embed_data_path, scheme="silx"
            )


class FileExtension(Enum):
    H5 = ".h5"
    HDF5 = ".hdf5"
    NX = ".nx"


class Format(Enum):
    STANDARD = "standard"
    XRD_CT = "xrd-ct"
    XRD_3D = "3d-xrd"


def get_file_name(file_name, extension, check=True):
    """
    set the given extension

    :param str file_name: name of the file
    :param str extension: extension to give
    :param bool check: if check, already check if the file as one of the
                       '_FileExtension'
    """
    extension = FileExtension.from_value(extension.lower())
    if check:
        for value in FileExtension.values():
            if file_name.lower().endswith(value):
                return file_name
    return file_name + extension.value()


class Progress:
    """Simple interface for defining advancement on a 100 percentage base"""

    def __init__(self, name: str):
        self._name = name
        self.set_name(name)

    def set_name(self, name):
        self._name = name
        self.reset()

    def reset(self, max_: typing.Union[None, int] = None) -> None:
        """
        reset the advancement to n and max advancement to max_
        :param int max_:
        """
        self._n_processed = 0
        self._max_processed = max_

    def start_process(self) -> None:
        self.set_advancement(0)

    def set_advancement(self, value: int) -> None:
        """

        :param int value: set advancement to value
        """
        length = 20  # modify this to change the length
        block = int(round(length * value / 100))
        blocks_str = "#" * block + "-" * (length - block)
        msg = "\r{0}: [{1}] {2}%".format(self._name, blocks_str, round(value, 2))
        if value >= 100:
            msg += " DONE\r\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def end_process(self) -> None:
        """Set advancement to 100 %"""
        self.set_advancement(100)

    def set_max_advancement(self, n: int) -> None:
        """

        :param int n: number of steps contained by the advancement. When
        advancement reach this value, advancement will be 100 %
        """
        self._max_processed = n

    def increase_advancement(self, i: int = 1) -> None:
        """

        :param int i: increase the advancement of n step
        """
        self._n_processed += i
        advancement = int(float(self._n_processed / self._max_processed) * 100)
        self.set_advancement(advancement)


def get_tuple_of_keys_from_cmd(cmd_value: str) -> tuple:
    """Return a tuple"""
    return tuple(cmd_value.split(","))


def is_nx_tomo_entry(file_path, entry):
    """

    :param str file_path: hdf5 file path
    :param str entry: entry to check
    :return: True if the entry is an NXTomo entry
    """
    if not os.path.exists(file_path):
        return False
    else:
        with HDF5File(file_path, mode="r") as h5s:
            if entry not in h5s:
                return False
            node = h5s[entry]
            return HDF5TomoScan.node_is_nxtomo(node)


def add_dark_flat_nx_file(
    file_path: str,
    entry: str,
    darks_start: typing.Union[None, numpy.ndarray, DataUrl] = None,
    flats_start: typing.Union[None, numpy.ndarray, DataUrl] = None,
    darks_end: typing.Union[None, numpy.ndarray, DataUrl] = None,
    flats_end: typing.Union[None, numpy.ndarray, DataUrl] = None,
    extras: typing.Union[None, dict] = None,
    logger: typing.Union[None, logging.Logger] = None,
    embed_data: bool = False,
):
    """
    This will get all data from entry@input_file and patch them with provided
    dark and / or flat(s).
    We consider the sequence as: dark, start_flat, projections, end_flat.

    Behavior regarding data type and target dataset:

    * if dataset at `entry` already exists:
        * if dataset at `entry` is a 'standard' dataset:
            * data will be loaded if necessary and `enrty` will be updated
        * if dataset at `entry` is a virtual dataset:
            * if `data` is a numpy array then we raise an error: the data should
              already be saved somewhere and you should provide a DataUrl
            * if `data` is a DataUrl then the virtual dataset is updated and
              a virtual source pointing to the
              DataUrl.file_path()@DataUrl.data_path() is added to the layout
    * if a new dataset `entry` need to be added:
        * if `data` is a numpy array then we create a new 'standard' Dataset
        * if `data` is a DataUrl then a new virtual dataset will be created

    note: Datasets `image_key`, `image_key_control`, `rotation_angle` and
    `count_time` will be copied each time.

    :param file_path: NXTomo file containing data to be patched
    :type file_path: str
    :param entry: entry to be patched
    :type entry: str
    :param darks_start: (3D) numpy array containing the first dark serie if any
    :type darks_start: Union[None, numpy.ndarray, DataUrl]
    :param flats_start: (3D) numpy array containing the first flat if any
    :type flats_start: Union[None, numpy.ndarray, DataUrl]
    :param darks_end: (3D) numpy array containing dark the second dark serie if
                      any
    :type darks_end: Union[None, numpy.ndarray, DataUrl]
    :param flats_end: (3D) numpy array containing the second flat if any
    :type flats_end: Union[None, numpy.ndarray, DataUrl]
    :param extras: dictionary to specify some parameters for flats and dark
                   like rotation angle.
                   valid keys: 'start_dark', 'end_dark', 'start_flag',
                   'end_flag'.
                   Values should be a dictionary of 'NXTomo' keys with
                   values to be set instead of 'default values'.
                   Possible values are:
                   * `count_time`
                   * `rotation_angle`
    :type extras: Union[None, dict]
    :param Union[None, logging.Logger] logger: object for logs
    :param bool embed_data: if True then each external data will be copy
                            under a 'duplicate_data' folder
    """
    if extras is None:
        extras = {}
    else:
        for key in extras:
            valid_extra_keys = ("darks_start", "darks_end", "flats_start", "flats_end")
            if key not in valid_extra_keys:
                raise ValueError(
                    "{key} is not recognized. Valid values are "
                    "{keys}".format(key=key, keys=valid_extra_keys)
                )

    if embed_data is True:
        darks_start = embed_url(darks_start, output_file=file_path)
        darks_end = embed_url(darks_end, output_file=file_path)
        flats_start = embed_url(flats_start, output_file=file_path)
        flats_end = embed_url(flats_end, output_file=file_path)
    else:
        for url in (darks_start, darks_end, flats_start, flats_end):
            if url is not None and isinstance(url, DataUrl):
                if isinstance(url.data_slice(), slice):
                    if url.data_slice().step not in (None, 1):
                        raise ValueError(
                            "When data is not embed slice `step`"
                            "must be None or 1. Other values are"
                            "not handled. Failing url is {}"
                            "".format(url)
                        )

    # !!! warning: order of dark / flat treatments import
    data_names = "flats_start", "darks_end", "flats_end", "darks_start"
    datas = flats_start, darks_end, flats_end, darks_start
    keys_value = (
        ImageKey.FLAT_FIELD.value,
        ImageKey.DARK_FIELD.value,
        ImageKey.FLAT_FIELD.value,
        ImageKey.DARK_FIELD.value,
    )
    wheres = "start", "end", "end", "start"  # warning: order import

    for d_n, data, key, where in zip(data_names, datas, keys_value, wheres):
        if data is None:
            continue
        n_frames_to_insert = 1
        if isinstance(data, numpy.ndarray) and data.ndim == 3:
            n_frames_to_insert = data.shape[0]
        elif isinstance(data, DataUrl):
            with HDF5File(data.file_path(), mode="r") as h5s:
                if data.data_path() not in h5s:
                    raise KeyError(
                        "Path given ({}) is not in {}".format(
                            data.data_path(), data.file_path
                        )
                    )
                data_node = get_data(data)
                if data_node.ndim == 3:
                    n_frames_to_insert = data_node.shape[0]
        else:
            raise TypeError("{} as input is not managed".format(type(data)))

        if logger is not None:
            logger.info(
                "insert {data_type} frame of type {key} at the"
                "{where}".format(data_type=type(data), key=key, where=where)
            )
        # update 'data' dataset
        data_path = os.path.join(entry, "instrument", "detector", "data")
        _FrameAppender(
            data, file_path, data_path=data_path, where=where, logger=logger
        ).process()
        # update image-key and image_key_control (we are not managing the
        # 'alignment projection here so values are identical')
        ik_path = os.path.join(entry, "instrument", "detector", "image_key")
        ikc_path = os.path.join(entry, "instrument", "detector", "image_key_control")
        for path in (ik_path, ikc_path):
            _FrameAppender(
                [key] * n_frames_to_insert,
                file_path,
                data_path=path,
                where=where,
                logger=logger,
            ).process()

        # add 'other' necessaries key:
        count_time_path = os.path.join(
            entry,
            "instrument",
            "detector",
            "count_time",
        )
        rotation_angle_path = os.path.join(entry, "sample", "rotation_angle")
        x_translation_path = os.path.join(entry, "sample", "x_translation")
        y_translation_path = os.path.join(entry, "sample", "y_translation")
        z_translation_path = os.path.join(entry, "sample", "z_translation")
        data_key_paths = (
            count_time_path,
            rotation_angle_path,
            x_translation_path,
            y_translation_path,
            z_translation_path,
        )
        mandatory_keys = (
            "count_time",
            "rotation_angle",
        )
        optional_keys = (
            "x_translation",
            "y_translation",
            "z_translation",
        )

        data_keys = tuple(list(mandatory_keys) + list(optional_keys))

        for data_key, data_key_path in zip(data_keys, data_key_paths):
            data_to_insert = None
            if d_n in extras and data_key in extras[d_n]:
                provided_value = extras[d_n][data_key]
                if isinstance(provided_value, Iterable):
                    if len(provided_value) != n_frames_to_insert:
                        raise ValueError(
                            "Given value to store from extras has"
                            " incoherent length({}) compare to "
                            "the number of frame to save ({})"
                            "".format(len(provided_value), n_frames_to_insert)
                        )
                    else:
                        data_to_insert = provided_value
                else:
                    try:
                        data_to_insert = [provided_value] * n_frames_to_insert
                    except Exception as e:
                        logger.error("Fail to create data to insert. Error is", e)
                        return
            else:
                # get default values
                def get_default_value(location, where_):
                    with HDF5File(file_path, mode="r") as h5s:
                        if location not in h5s:
                            return None
                        existing_data = h5s[location]
                        if where_ == "start":
                            return existing_data[0]
                        else:
                            return existing_data[-1]

                try:
                    default_value = get_default_value(data_key_path, where)
                except:
                    default_value = None
                if default_value is None:
                    msg = (
                        "Unable to define a default value for {}. Location "
                        "empty in {}.".format(data_key_path, file_path)
                    )
                    if data_key in mandatory_keys:
                        raise ValueError(msg)
                    elif logger:
                        logger.warning(msg)
                    continue
                elif logger:
                    logger.debug(
                        "No value(s) provided for {path}. "
                        "Extract some default value ({def_value})."
                        "".format(path=data_key_path, def_value=default_value)
                    )
                data_to_insert = [default_value] * n_frames_to_insert

            if data_to_insert is not None:
                _FrameAppender(
                    data_to_insert,
                    file_path,
                    data_path=data_key_path,
                    where=where,
                    logger=logger,
                ).process()


class _FrameAppender:
    """
    Class to insert 2D frame(s) to an existing dataset
    """

    def __init__(self, data, file_path, data_path, where, logger=None):
        if where not in ("start", "end"):
            raise ValueError("`where` should be `start` or `end`")

        if not isinstance(data, (DataUrl, numpy.ndarray, list, tuple)):
            raise TypeError(
                "data should be an instance of DataUrl or a numpy "
                "array not {}".format(type(data))
            )

        self.data = data
        self.file_path = os.path.realpath(file_path)
        self.data_path = data_path
        self.where = where
        self.logger = logger

    def process(self) -> None:
        """
        main function. Will start the insertion of frame(s)
        """
        with HDF5File(self.file_path, mode="a") as h5s:
            if self.data_path in h5s:
                self._add_to_existing_dataset(h5s)
            else:
                self._create_new_dataset(h5s)
            if self.logger:
                self.logger.info(
                    "data added to {entry}@{file_path}"
                    "".format(entry=self.data_path, file_path=self.file_path)
                )

    def _add_to_existing_virtual_dataset(self, h5s):
        if (
            h5py.version.hdf5_version_tuple[0] <= 1
            and h5py.version.hdf5_version_tuple[1] < 12
        ):
            if self.logger:
                self.logger.warning(
                    "You are working on virtual dataset"
                    "with a hdf5 version < 12. Frame "
                    "you want to change might be "
                    "modified depending on the working "
                    "directory without notifying."
                    "See https://github.com/silx-kit/silx/issues/3277"
                )
        if isinstance(self.data, (numpy.ndarray, list, tuple)):
            raise TypeError(
                "Provided data is a numpy array when given"
                "dataset path is a virtual dataset. "
                "You must store the data somewhere else "
                "and provide a DataUrl"
            )
        else:
            if self.logger is not None:
                self.logger.debug(
                    "Update virtual dataset: "
                    "{entry}@{file_path}"
                    "".format(entry=self.data_path, file_path=self.file_path)
                )
            # store DataUrl in the current virtual dataset
            url = self.data

            from nxtomomill.converter.hdf5.acquisition.baseacquisition import (
                DatasetReader,
            )

            def check_dataset(dataset_frm_url):
                data_need_reshape = False
                """check if the dataset is valid or might need a reshape"""
                if not dataset_frm_url.ndim in (2, 3):
                    raise ValueError(
                        "{} should point to 2D or 3D dataset ".format(url.path())
                    )
                if dataset_frm_url.ndim == 2:
                    new_shape = 1, dataset_frm_url.shape[0], dataset_frm_url.shape[1]
                    if self.logger is not None:
                        self.logger.info(
                            "reshape provided data to 3D (from {} to {})"
                            "".format(dataset_frm_url.shape, new_shape)
                        )
                    data_need_reshape = True
                return data_need_reshape

            loaded_dataset = None
            if url.data_slice() is None:
                # case we can avoid to load the data in memory
                with DatasetReader(url) as data_frm_url:
                    data_need_reshape = check_dataset(data_frm_url)
            else:
                data_frm_url = get_data(url)
                data_need_reshape = check_dataset(data_frm_url)
                loaded_dataset = data_frm_url

            if url.data_slice() is None and not data_need_reshape:
                # case we can avoid to load the data in memory
                with DatasetReader(self.data) as data_frm_url:
                    self.__insert_in_vds(h5s, url, data_frm_url)
            else:
                if loaded_dataset is None:
                    data_frm_url = get_data(url)
                else:
                    data_frm_url = loaded_dataset
                self.__insert_in_vds(h5s, url, data_frm_url)

    def __insert_in_vds(self, h5s, url, data_frm_url):
        if data_frm_url.ndim == 2:
            n_frames = 1
            dim_2, dim_1 = data_frm_url.shape
            data_frm_url = data_frm_url.reshape(1, dim_2, dim_1)
        elif data_frm_url.ndim == 3:
            n_frames, dim_2, dim_1 = data_frm_url.shape
        else:
            raise ValueError("data to had is expected to be 2 or 3 d")

        virtual_sources_len = []
        virtual_sources = []
        # we need to recreate the VirtualSource they are not
        # store or available from the API
        for vs_info in h5s[self.data_path].virtual_sources():
            length, vs = self._recreate_vs(vs_info=vs_info, vds_file=self.file_path)
            virtual_sources.append(vs)
            virtual_sources_len.append(length)

        vds_file_path = os.path.abspath(os.path.relpath(url.file_path(), os.getcwd()))
        vds_file_path = os.path.realpath(vds_file_path)
        vds_file_path = os.path.relpath(vds_file_path, os.path.dirname(self.file_path))
        if not vds_file_path.startswith("./"):
            vds_file_path = "./" + vds_file_path

        new_virtual_source = h5py.VirtualSource(
            path_or_dataset=vds_file_path,
            name=url.data_path(),
            shape=data_frm_url.shape,
        )

        if url.data_slice() is not None:
            # in the case we have to process to a FancySelection
            with HDF5File(os.path.abspath(url.file_path()), mode="r") as h5sd:
                dst = h5sd[url.data_path()]
                sel = selection.select(
                    h5sd[url.data_path()].shape, url.data_slice(), dst
                )
                new_virtual_source.sel = sel

        n_frames += h5s[self.data_path].shape[0]
        data_type = h5s[self.data_path].dtype

        if self.where == "start":
            virtual_sources.insert(0, new_virtual_source)
            virtual_sources_len.insert(0, data_frm_url.shape[0])
        else:
            virtual_sources.append(new_virtual_source)
            virtual_sources_len.append(data_frm_url.shape[0])

        # create the new virtual dataset
        layout = h5py.VirtualLayout(shape=(n_frames, dim_2, dim_1), dtype=data_type)
        last = 0
        for v_source, vs_len in zip(virtual_sources, virtual_sources_len):
            layout[last : vs_len + last] = v_source
            last += vs_len
        if self.data_path in h5s:
            del h5s[self.data_path]
        h5s.create_virtual_dataset(self.data_path, layout)

    def _add_to_existing_none_virtual_dataset(self, h5s):
        """
        for now when we want to add data *to a none virtual dataset*
        we always duplicate data if provided from a DataUrl.
        We could create a virtual dataset as well but seems to complicated for
        a use case that we don't really have at the moment.

        :param h5s:
        """
        if self.logger is not None:
            self.logger.debug("Update dataset: {entry}@{file_path}")
        if isinstance(self.data, (numpy.ndarray, list, tuple)):
            new_data = self.data
        else:
            url = self.data
            new_data = get_data(url)

        if isinstance(new_data, numpy.ndarray):
            if not new_data.shape[1:] == h5s[self.data_path].shape[1:]:
                raise ValueError(
                    "Data shapes are incoherent: {} vs {}".format(
                        new_data.shape, h5s[self.data_path].shape
                    )
                )

            new_shape = (
                new_data.shape[0] + h5s[self.data_path].shape[0],
                new_data.shape[1],
                new_data.shape[2],
            )
            data_to_store = numpy.empty(new_shape)
            if self.where == "start":
                data_to_store[: new_data.shape[0]] = new_data
                data_to_store[new_data.shape[0] :] = h5py_read_dataset(
                    h5s[self.data_path]
                )
            else:
                data_to_store[: h5s[self.data_path].shape[0]] = h5py_read_dataset(
                    h5s[self.data_path]
                )
                data_to_store[h5s[self.data_path].shape[0] :] = new_data
        else:
            assert isinstance(
                self.data, (list, tuple)
            ), "Unmanaged data type {}".format(type(self.data))
            o_data = h5s[self.data_path]
            o_data = list(h5py_read_dataset(o_data))
            if self.where == "start":
                new_data.extend(o_data)
                data_to_store = numpy.asarray(new_data)
            else:
                o_data.extend(new_data)
                data_to_store = numpy.asarray(o_data)

        del h5s[self.data_path]
        h5s[self.data_path] = data_to_store

    def _add_to_existing_dataset(self, h5s):
        """Add the frame to an existing dataset"""
        if h5s[self.data_path].is_virtual:
            self._add_to_existing_virtual_dataset(h5s=h5s)
        else:
            self._add_to_existing_none_virtual_dataset(h5s=h5s)

    def _create_new_dataset(self, h5s):
        """
        needs to create a new dataset. In this case the policy is:
           - if a DataUrl is provided then we create a virtual dataset
           - if a numpy array is provided then we create a 'standard' dataset
        """

        if isinstance(self.data, DataUrl):
            url = self.data

            with HDF5File(url.file_path(), mode="r") as o_h5s:
                if not o_h5s[url.data_path()].ndim in (2, 3):
                    raise ValueError(
                        "{} should point to 2D or 3D dataset ".format(url.path())
                    )
                data_shape = o_h5s[url.data_path()].shape
                data_type = o_h5s[url.data_path()].dtype
                if len(data_shape) == 2:
                    data_shape = (1, data_shape[0], data_shape[1])
                layout = h5py.VirtualLayout(shape=data_shape, dtype=data_type)
                layout[:] = h5py.VirtualSource(
                    url.file_path(), url.data_path(), shape=data_shape
                )
                h5s.create_virtual_dataset(self.data_path, layout)
        else:
            h5s[self.data_path] = self.data

    @staticmethod
    def _recreate_vs(vs_info, vds_file):
        """Simple util to retrieve a h5py.VirtualSource from virtual source
        information.

        to understand clearly this function you might first have a look at
        the use case exposed in issue:
        https://gitlab.esrf.fr/tomotools/nxtomomill/-/issues/40
        """
        with cwd_context():
            if os.path.dirname(vds_file) not in ("", None):
                os.chdir(os.path.dirname(vds_file))
            with HDF5File(vs_info.file_name, mode="r") as vs_node:
                dataset = vs_node[vs_info.dset_name]
                select_bounds = vs_info.vspace.get_select_bounds()
                left_bound = select_bounds[0]
                right_bound = select_bounds[1]
                length = right_bound[0] - left_bound[0] + 1
                # warning: for now step is not managed with virtual
                # dataset

                virtual_source = h5py.VirtualSource(
                    vs_info.file_name,
                    vs_info.dset_name,
                    shape=dataset.shape,
                )
                # here we could provide dataset but we won't to
                # insure file path will be relative.
                type_code = vs_info.src_space.get_select_type()
                # check for unlimited selections in case where selection is regular
                # hyperslab, which is the only allowed case for h5s.UNLIMITED to be
                # in the selection
                if (
                    type_code == h5py_h5s.SEL_HYPERSLABS
                    and vs_info.src_space.is_regular_hyperslab()
                ):
                    (
                        source_start,
                        stride,
                        count,
                        block,
                    ) = vs_info.src_space.get_regular_hyperslab()
                    source_end = source_start[0] + length

                    sel = selection.select(
                        dataset.shape,
                        slice(source_start[0], source_end),
                        dataset=dataset,
                    )
                    virtual_source.sel = sel

                return (
                    length,
                    virtual_source,
                )


@deprecated(replacement="_FrameAppender", since_version="0.5.0")
def _insert_frame_data(data, file_path, data_path, where, logger=None):
    """
    This function is used to insert some frame(s) (numpy 2D or 3D to an
    existing dataset. Before the existing array or After.

    :param data:
    :param file_path:
    :param data_path: If the path point to a virtual dataset them this one
                      will be updated but data should be a DataUrl. Of the
                      same shape. Else we will update the data_path by
                      extending the dataset.
    :param where:
    :raises TypeError: In the case the data type and existing data_path are
                       incompatible.
    """
    fa = _FrameAppender(
        data=data, file_path=file_path, data_path=data_path, where=where, logger=logger
    )
    return fa.process()


def change_image_key_control(
    file_path: str,
    entry: str,
    frames_indexes: typing.Union[slice, Iterable],
    image_key_control_value: typing.Union[int, ImageKey],
    logger=None,
):
    """
    Will modify image_key and image_key_control values for the requested
    frames.

    :param str file_path: path the nexus file
    :param str entry: name of the entry to modify
    :param frames_indexes: index of the frame for which we want to modify
                           the image key
    :type frames_indexes: Union[slice, Iterable]
    :param image_key_control_value:
    :type image_key_control_value: Union[int, ImageKey]
    :param logging.Logger logger: logger
    """
    if not isinstance(frames_indexes, (Iterable, slice)):
        raise TypeError("`frame_indexes` should be an instance of Iterable slice")
    if logger:
        logger.info(
            "Update frames {frames_indexes} to"
            "{image_key_control_value} of {entry}@{file_path}"
            "".format(
                frames_indexes=frames_indexes,
                image_key_control_value=image_key_control_value,
                entry=entry,
                file_path=file_path,
            )
        )

    image_key_control_value = ImageKey.from_value(image_key_control_value)
    with HDF5File(file_path, mode="a") as h5s:
        node = h5s[entry]
        image_keys_path = "/".join(("instrument", "detector", "image_key"))
        image_keys = h5py_read_dataset(node[image_keys_path])
        image_keys_control_path = "/".join(
            ("instrument", "detector", "image_key_control")
        )
        image_keys_control = h5py_read_dataset(node[image_keys_control_path])
        # filter frame indexes
        if isinstance(frames_indexes, slice):
            step = frames_indexes.step
            if step is None:
                step = 1
            stop = frames_indexes.stop
            if stop in (None, -1):
                stop = len(image_keys)
            frames_indexes = list(range(frames_indexes.start, stop, step))
        frames_indexes = list(
            filter(lambda x: 0 <= x <= len(image_keys_control), frames_indexes)
        )
        # manage image_key_control
        image_keys_control[frames_indexes] = image_key_control_value.value
        node[image_keys_control_path][:] = image_keys_control
        # manage image_key. In this case we should get rid of Alignment values
        # and replace it by Projection values
        image_key_value = image_key_control_value
        if image_key_value is ImageKey.ALIGNMENT:
            image_key_value = ImageKey.PROJECTION
        image_keys[frames_indexes] = image_key_value.value
        node[image_keys_path][:] = image_keys
