# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2020 European Synchrotron Radiation Facility
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
#############################################################################*/


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "10/10/2019"


import os
import fabio
from silx.io.url import DataUrl
from tomoscan.scanbase import TomoScanBase
from typing import Union
from typing import Iterable
import numpy
import logging
import sys
from tomoscan.io import HDF5File
import warnings
import contextlib


_logger = logging.getLogger(__name__)


def get_parameters_frm_par_or_info(file_: str) -> dict:
    """
    Create a dictionary from the file with the information name as keys and
    their values as values

    :param file_: path to the file to parse
    :type file_: str
    :raises: ValueError when fail to parse some line.
    """
    assert os.path.exists(file_) and os.path.isfile(file_)
    ddict = {}
    f = open(file_, "r")
    lines = f.readlines()
    for line in lines:
        if not "=" in line:
            continue
        l = line.replace(" ", "")
        l = l.rstrip("\n")
        # remove on the line comments
        if "#" in l:
            l = l.split("#")[0]
        if l == "":
            continue
        try:
            key, value = l.split("=")
        except ValueError as e:
            raise ValueError('fail to extract information from "%s"' % l)
        else:
            ddict[key.lower()] = value
    return ddict


def extract_urls_from_edf(
    file_: str, start_index: Union[None, int], n_frames: Union[int, None] = None
) -> dict:
    """
    return one DataUrl for each frame contain in the file_

    :param file_: path to the file to parse
    :type file_: str
    :param n_frames: Number of frames in each edf file (inferred if not told)
    :type n_frames: Union[int, None]
    :param start_index:
    :type start_index: Union[None,start_index]
    """
    res = {}
    index = 0 if start_index is None else start_index
    if n_frames is None:
        with fabio.open(file_) as fabio_file:
            n_frames = fabio_file.nframes
    for i_frame in range(n_frames):
        res[index] = DataUrl(
            scheme="fabio",
            file_path=file_,
            data_slice=[
                i_frame,
            ],
        )
        index += 1
    return res


def get_compacted_dataslices(
    urls: dict, max_grp_size=None, return_merged_indices=False, return_url_set=False
):
    """
    Regroup urls to get the data more efficiently.
    Build a structure mapping files indices to information on
    how to load the data: `{indices_set: data_location}`
    where `data_location` contains contiguous indices.

    :param dict urls: Dictionary where the key is an integer and the value is
                      a silx `DataUrl`.
    :param max_grp_size: maximum size of url grps
    :type max_grp_size: None or int
    :param bool return_merged_indices: if True return the last merged indices.
                                       Deprecated
    :param bool return_url_set: return a set with url containing `urls` slices
                                and data path

    :return: Dictionary where the key is a list of indices, and the value is
             the corresponding `silx.io.url.DataUrl` with merged data_slice
    :rtype: dict
    """

    def _convert_to_slice(idx):
        if numpy.isscalar(idx):
            return slice(idx, idx + 1)
        # otherwise, assume already slice object
        return idx

    def is_contiguous_slice(slice1, slice2):
        if numpy.isscalar(slice1):
            slice1 = slice(slice1, slice1 + 1)
        if numpy.isscalar(slice2):
            slice2 = slice(slice2, slice2 + 1)
        return slice2.start == slice1.stop

    def merge_slices(slice1, slice2):
        return slice(slice1.start, slice2.stop)

    if return_merged_indices is True:
        warnings.warn(
            "return_merged_indices is deprecated. It will be removed in version 0.8"
        )

    if max_grp_size is None:
        max_grp_size = sys.maxsize

    sorted_files_indices = sorted(urls.keys())
    idx0 = sorted_files_indices[0]
    first_url = urls[idx0]
    merged_indices = [[idx0]]
    data_location = [
        [
            first_url.file_path(),
            first_url.data_path(),
            _convert_to_slice(first_url.data_slice()),
            first_url.scheme(),
        ]
    ]
    pos = 0
    grp_size = 0
    curr_fp, curr_dp, curr_slice, curr_scheme = data_location[pos]
    for idx in sorted_files_indices[1:]:
        url = urls[idx]
        next_slice = _convert_to_slice(url.data_slice())
        if (
            (grp_size <= max_grp_size)
            and (url.file_path() == curr_fp)
            and (url.data_path() == curr_dp)
            and is_contiguous_slice(curr_slice, next_slice)
            and (url.scheme() == curr_scheme)
        ):
            merged_indices[pos].append(idx)
            merged_slices = merge_slices(curr_slice, next_slice)
            data_location[pos][-2] = merged_slices
            curr_slice = merged_slices
            grp_size += 1
        else:  # "jump"
            pos += 1
            merged_indices.append([idx])
            data_location.append(
                [
                    url.file_path(),
                    url.data_path(),
                    _convert_to_slice(url.data_slice()),
                    url.scheme(),
                ]
            )
            curr_fp, curr_dp, curr_slice, curr_scheme = data_location[pos]
            grp_size = 0

    # Format result
    res = {}
    for ind, dl in zip(merged_indices, data_location):
        res.update(
            dict.fromkeys(
                ind,
                DataUrl(
                    file_path=dl[0], data_path=dl[1], data_slice=dl[2], scheme=dl[3]
                ),
            )
        )

    if return_url_set:
        url_set = {}
        for _, url in res.items():
            path = url.file_path(), url.data_path(), str(url.data_slice())
            url_set[url.file_path(), url.data_path(), str(url.data_slice())] = url

        if return_merged_indices:
            return res, merge_slices, url_set
        else:
            return res, url_set

    if return_merged_indices:
        return res, merged_slices
    else:
        return res


def from_sequences_to_grps(scans: Iterable) -> tuple:
    """
    create group with the same sample name

    :param Iterable scans:
    :return: tuple of group of scans
    """
    grps = {}
    for scan in scans:
        if not isinstance(scan, TomoScanBase):
            raise TypeError("Elements are expected to be instance of " "TomoScanBase")
        if scan.sample_name in grps:
            grps[scan.sample_name].append(scan)
        else:
            grps[scan.sample_name] = [
                scan,
            ]
    return tuple(grps.values())


def check_grp_is_valid(scans: Iterable):
    """
    Insure the provided group of scan is valid. Otherwise raise an error

    :param Iterable scans: group of TomoScanBAse to check
    """
    l_scans = set()
    for scan in scans:
        if not isinstance(scan, TomoScanBase):
            raise TypeError("Elements are expected to be instance of " "TomoScanBase")
        if scan in l_scans:
            raise ValueError("{} is present at least twice")
        elif len(l_scans) > 0:
            if list(l_scans)[0].sample_name != scan.sample_name:
                raise ValueError(
                    "{} and {} are from two different sample".format(scan, l_scans)
                )
        l_scans.add(scan)


def grp_is_complete(scans: Iterable) -> bool:
    """
    Insure the provided group of scan is valid. Otherwise raise an error

    :param Iterable scans: group of TomoScanBAse to check
    :return: True if the group is complete
    :rtype: bool
    """
    if len(scans) == 0:
        return True
    try:
        check_grp_is_valid(scans=scans)
    except Exception as e:
        _logger.error("provided group is invalid. {}".format(e))
    else:
        group_size = list(scans)[0].group_size
        if group_size is None:
            _logger.warning("No information found regarding group size")
            return True
        elif group_size == len(scans):
            return True
        elif group_size < len(scans):
            _logger.warning("more scans found than group_size")
            return True
        else:
            return False


def dataset_has_broken_vds(url: DataUrl):
    """
    check that the provided url is not a VDS with broken links.
    """
    if not isinstance(url, DataUrl):
        raise TypeError(f"{url} is expected to be an instance of {DataUrl}")
    with HDF5File(url.file_path(), mode="r") as h5f:
        dataset = h5f[url.data_path()]
        if not dataset.is_virtual:
            return False
        else:
            for file_ in get_unique_files_linked(url=url):
                if not os.path.exists(file_):
                    _logger.warning(f"{file_} does not exists")
                    return True
    return False


def get_datasets_linked_to_vds(url: DataUrl):
    """
    Return set([file-path, data_path]) linked to the provided url
    """
    if not isinstance(url, DataUrl):
        raise TypeError(f"{url} is expected to be an instance of {DataUrl}")

    start_file_path = url.file_path()
    start_dataset_path = url.data_path()
    start_dataset_slice = url.data_slice()
    if isinstance(start_dataset_slice, slice):
        start_dataset_slice = tuple(
            range(
                start_dataset_slice.start,
                start_dataset_slice.stop,
                start_dataset_slice.step or 1,
            )
        )
    print("inital dataset_slice is", start_dataset_slice[0], start_dataset_slice[-1])

    virtual_dataset_to_treat = set()
    final_dataset = set()
    already_checked = set()

    # first datasets to be tested
    virtual_dataset_to_treat.add(
        (start_file_path, start_dataset_path, start_dataset_slice),
    )

    while len(virtual_dataset_to_treat) > 0:
        to_treat = list(virtual_dataset_to_treat)
        virtual_dataset_to_treat.clear()

        for (file_path, dataset_path, dataset_slice) in to_treat:
            if (file_path, dataset_path, dataset_slice) in already_checked:
                continue
            if os.path.exists(file_path):
                with HDF5File(file_path, mode="r") as h5f:
                    dataset = h5f[dataset_path]
                    if dataset.is_virtual:
                        for vs_info in dataset.virtual_sources():
                            min_frame_bound = vs_info.vspace.get_select_bounds()[0][0]
                            max_frame_bound = vs_info.vspace.get_select_bounds()[1][0]
                            if isinstance(dataset_slice, int):
                                if (
                                    not min_frame_bound
                                    <= dataset_slice
                                    <= max_frame_bound
                                ):
                                    continue
                            elif isinstance(dataset_slice, tuple):
                                if (
                                    min_frame_bound > dataset_slice[-1]
                                    or max_frame_bound < dataset_slice[0]
                                ):
                                    continue

                            with cwd_context():
                                os.chdir(os.path.dirname(file_path))
                                # Fixme: For now will look at the entire dataset of the n +1 file.
                                # if those can also contains virtual dataset and we want to handle
                                # the case a part of it is broken but not ours this should handle
                                # hyperslab
                                virtual_dataset_to_treat.add(
                                    (
                                        os.path.realpath(vs_info.file_name),
                                        vs_info.dset_name,
                                        None,
                                    )
                                )
                    else:
                        final_dataset.add((file_path, dataset_path, dataset_slice))
            else:
                final_dataset.add((file_path, dataset_path, dataset_slice))
            already_checked.add((file_path, dataset_path, dataset_slice))
    return final_dataset


def get_unique_files_linked(url: DataUrl):
    """
    Return the list of unique files linked to the DataUrl without depth limitation
    """
    unique_files = set()
    datasets_linked = get_datasets_linked_to_vds(url=url)
    [unique_files.add(file_path) for (file_path, _, _) in datasets_linked]
    return unique_files


@contextlib.contextmanager
def cwd_context():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)
