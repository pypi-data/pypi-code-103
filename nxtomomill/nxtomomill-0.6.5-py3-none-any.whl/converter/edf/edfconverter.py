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
module to convert from edf to (nexus tomo compliant) .nx
"""

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "27/11/2020"


from collections import namedtuple
from nxtomomill import utils
from nxtomomill.utils import ImageKey
from nxtomomill.converter.version import version as converter_version
from nxtomomill.converter.utils import create_nx_data_group
from nxtomomill.converter.utils import link_nxbeam_to_root
from nxtomomill.settings import Tomo
from tomoscan.esrf.edfscan import EDFTomoScan
from tomoscan.unitsystem import metricsystem
from tomoscan.io import HDF5File
import fabio
import numpy
import os

EDF_MOTOR_POS = Tomo.EDF.MOTOR_POS
EDF_MOTOR_MNE = Tomo.EDF.MOTOR_MNE
EDF_REFS_NAMES = Tomo.EDF.REFS_NAMES
EDF_TO_IGNORE = Tomo.EDF.TO_IGNORE
EDF_ROT_ANGLE = Tomo.EDF.ROT_ANGLE
EDF_DARK_NAMES = Tomo.EDF.DARK_NAMES
EDF_X_TRANS = Tomo.EDF.X_TRANS
EDF_Y_TRANS = Tomo.EDF.Y_TRANS
EDF_Z_TRANS = Tomo.EDF.Z_TRANS

import logging

_logger = logging.getLogger(__name__)


EDFFileKeys = namedtuple(
    "EDFFileKeys",
    [
        "motor_pos_key",
        "motor_mne_key",
        "rot_angle_key",
        "x_trans_key",
        "y_trans_key",
        "z_trans_key",
        "to_ignore",
        "dark_names",
        "ref_names",
    ],
)

DEFAULT_EDF_KEYS = EDFFileKeys(
    EDF_MOTOR_POS,
    EDF_MOTOR_MNE,
    EDF_ROT_ANGLE,
    EDF_X_TRANS,
    EDF_Y_TRANS,
    EDF_Z_TRANS,
    EDF_TO_IGNORE,
    EDF_DARK_NAMES,
    EDF_REFS_NAMES,
)


def edf_to_nx(
    scan: EDFTomoScan,
    output_file: str,
    file_extension: str,
    file_keys: EDFFileKeys = DEFAULT_EDF_KEYS,
    progress=None,
) -> tuple:
    """
    Convert an edf file to a nexus file.
    For now duplicate data.

    :param scan:
    :param output_file:
    :param file_extension:
    :param file_keys:
    :param progress:
    :return: (nexus_file, entry)
    :rtype:tuple
    """
    if not isinstance(scan, EDFTomoScan):
        raise TypeError("scan should be an instance of {}".format(EDFTomoScan))
    # in old data, rot ange is unknown. Compute it as a function of the proj number
    compute_rotangle = True

    fileout_h5 = utils.get_file_name(
        file_name=output_file, extension=file_extension, check=True
    )
    _logger.info("Output file will be " + fileout_h5)

    DARK_ACCUM_FACT = True
    with HDF5File(fileout_h5, "w") as h5d:
        proj_urls = scan.get_proj_urls(scan=scan.path)

        for dark_to_find in file_keys.dark_names:
            dk_urls = scan.get_darks_url(scan_path=scan.path, prefix=dark_to_find)
            if len(dk_urls) > 0:
                if dark_to_find == "dark":
                    DARK_ACCUM_FACT = False
                break
        _edf_to_ignore = list(file_keys.to_ignore)
        for refs_to_find in file_keys.ref_names:
            if refs_to_find == "ref":
                _edf_to_ignore.append("HST")
            else:
                _edf_to_ignore.remove("HST")
            refs_urls = scan.get_refs_url(
                scan_path=scan.path, prefix=refs_to_find, ignore=_edf_to_ignore
            )
            if len(refs_urls) > 0:
                break

        n_frames = len(proj_urls) + len(refs_urls) + len(dk_urls)

        # TODO: should be managed by tomoscan as well
        def getExtraInfo(scan):
            projections_urls = scan.projections
            indexes = sorted(projections_urls.keys())
            first_proj_file = projections_urls[indexes[0]]
            fid = fabio.open(first_proj_file.file_path())
            if hasattr(fid, "header"):
                hd = fid.header
            else:
                hd = fid.getHeader()
            try:
                rotangle_index = (
                    hd[file_keys.motor_mne_key]
                    .split(" ")
                    .index(file_keys.rot_angle_key)
                )
            except:
                rotangle_index = -1
            try:
                xtrans_index = (
                    hd[file_keys.motor_mne_key].split(" ").index(file_keys.x_trans_key)
                )
            except:
                xtrans_index = -1
            try:
                ytrans_index = (
                    hd[file_keys.motor_mne_key].split(" ").index(file_keys.y_trans_key)
                )
            except:
                ytrans_index = -1
            try:
                ztrans_index = (
                    hd[file_keys.motor_mne_key].split(" ").index(file_keys.z_trans_key)
                )
            except:
                ztrans_index = -1

            if hasattr(fid, "bytecode"):
                frame_type = fid.bytecode
            else:
                frame_type = fid.getByteCode()
            return frame_type, rotangle_index, xtrans_index, ytrans_index, ztrans_index

        (
            frame_type,
            rot_angle_index,
            x_trans_index,
            y_trans_index,
            z_trans_index,
        ) = getExtraInfo(scan=scan)

        data_dataset = h5d.create_dataset(
            "/entry/instrument/detector/data",
            shape=(n_frames, scan.dim_2, scan.dim_1),
            dtype=frame_type,
        )

        keys_dataset = h5d.create_dataset(
            "/entry/instrument/detector/image_key", shape=(n_frames,), dtype=numpy.int32
        )

        keys_control_dataset = h5d.create_dataset(
            "/entry/instrument/detector/image_key_control",
            shape=(n_frames,),
            dtype=numpy.int32,
        )

        h5d["/entry/sample/name"] = os.path.basename(scan.path)

        proj_angle = scan.scan_range / scan.tomo_n

        distance = scan.retrieve_information(
            scan=os.path.abspath(scan.path),
            ref_file=None,
            key="Distance",
            type_=float,
            key_aliases=["distance"],
        )
        if distance is not None:
            h5d["/entry/instrument/detector/distance"] = distance
            h5d["/entry/instrument/detector/distance"].attrs["unit"] = u"m"

        pixel_size = scan.retrieve_information(
            scan=os.path.abspath(scan.path),
            ref_file=None,
            key="PixelSize",
            type_=float,
            key_aliases=["pixelSize"],
        )
        h5d["/entry/instrument/detector/x_pixel_size"] = (
            pixel_size * metricsystem.millimeter.value
        )
        h5d["/entry/instrument/detector/x_pixel_size"].attrs["unit"] = u"m"
        h5d["/entry/instrument/detector/y_pixel_size"] = (
            pixel_size * metricsystem.millimeter.value
        )
        h5d["/entry/instrument/detector/y_pixel_size"].attrs["unit"] = u"m"

        energy = scan.retrieve_information(
            scan=os.path.abspath(scan.path),
            ref_file=None,
            key="Energy",
            type_=float,
            key_aliases=["energy"],
        )
        if energy is not None:
            h5d["/entry/instrument/beam/incident_energy"] = energy
            h5d["/entry/instrument/beam/incident_energy"].attrs["unit"] = u"keV"

        # rotations values
        rotation_dataset = h5d.create_dataset(
            "/entry/sample/rotation_angle", shape=(n_frames,), dtype=numpy.float32
        )
        h5d["/entry/sample/rotation_angle"].attrs["unit"] = "degree"

        # provision for centering motors
        x_dataset = h5d.create_dataset(
            "/entry/sample/x_translation", shape=(n_frames,), dtype=numpy.float32
        )
        h5d["/entry/sample/x_translation"].attrs["unit"] = "m"
        y_dataset = h5d.create_dataset(
            "/entry/sample/y_translation", shape=(n_frames,), dtype=numpy.float32
        )
        h5d["/entry/sample/y_translation"].attrs["unit"] = "m"
        z_dataset = h5d.create_dataset(
            "/entry/sample/z_translation", shape=(n_frames,), dtype=numpy.float32
        )
        h5d["/entry/sample/z_translation"].attrs["unit"] = "m"

        #  --------->  and now fill all datasets!

        nf = 0

        def read_url(url) -> tuple:
            data_slice = url.data_slice()
            if data_slice is None:
                data_slice = (0,)
            if data_slice is None or len(data_slice) != 1:
                raise ValueError(
                    "Fabio slice expect a single frame, " "but %s found" % data_slice
                )
            index = data_slice[0]
            if not isinstance(index, int):
                raise ValueError(
                    "Fabio slice expect a single integer, " "but %s found" % data_slice
                )

            try:
                fabio_file = fabio.open(url.file_path())
            except Exception:
                _logger.debug(
                    "Error while opening %s with fabio", url.file_path(), exc_info=True
                )
                raise IOError(
                    "Error while opening %s with fabio (use debug"
                    " for more information)" % url.path()
                )

            if fabio_file.nframes == 1:
                if index != 0:
                    raise ValueError(
                        "Only a single frame available. Slice %s out of range" % index
                    )
                data = fabio_file.data
                header = fabio_file.header
            else:
                data = fabio_file.getframe(index).data
                header = fabio_file.getframe(index).header

            fabio_file.close()
            fabio_file = None
            return data, header

        if progress is not None:
            progress.set_name("write dark")
            progress.set_max_advancement(len(dk_urls))

        def ignore(file_name):
            for forbid in _edf_to_ignore:
                if forbid in file_name:
                    return True
            return False

        # darks

        # dark in acumulation mode?
        norm_dark = 1.0
        if scan.dark_n > 0 and DARK_ACCUM_FACT is True:
            norm_dark = len(dk_urls) / scan.dark_n
        dk_indexes = sorted(dk_urls.keys())
        if progress is not None:
            progress.set_max_advancement(len(dk_urls))
        for dk_index in dk_indexes:
            dk_url = dk_urls[dk_index]
            if ignore(os.path.basename(dk_url.file_path())):
                _logger.info("ignore " + dk_url.file_path())
                continue
            data, header = read_url(dk_url)
            data_dataset[nf, :, :] = data * norm_dark
            keys_dataset[nf] = ImageKey.DARK_FIELD.value
            keys_control_dataset[nf] = ImageKey.DARK_FIELD.value

            if file_keys.motor_pos_key in header:
                str_mot_val = header[file_keys.motor_pos_key].split(" ")
                if rot_angle_index == -1:
                    rotation_dataset[nf] = 0.0
                else:
                    rotation_dataset[nf] = float(str_mot_val[rot_angle_index])
                if x_trans_index == -1:
                    x_dataset[nf] = 0.0
                else:
                    x_dataset[nf] = (
                        float(str_mot_val[x_trans_index])
                        * metricsystem.millimeter.value
                    )
                if y_trans_index == -1:
                    y_dataset[nf] = 0.0
                else:
                    y_dataset[nf] = (
                        float(str_mot_val[y_trans_index])
                        * metricsystem.millimeter.value
                    )
                if z_trans_index == -1:
                    z_dataset[nf] = 0.0
                else:
                    z_dataset[nf] = (
                        float(str_mot_val[z_trans_index])
                        * metricsystem.millimeter.value
                    )

            nf += 1
            if progress is not None:
                progress.increase_advancement(i=1)

        ref_indexes = sorted(refs_urls.keys())

        ref_projs = []
        for irf in ref_indexes:
            pjnum = int(irf)
            if pjnum not in ref_projs:
                ref_projs.append(pjnum)

        # refs
        def store_refs(
            refIndexes,
            tomoN,
            projnum,
            refUrls,
            nF,
            dataDataset,
            keysDataset,
            keysCDataset,
            xDataset,
            yDataset,
            zDataset,
            rotationDataset,
            raix,
            xtix,
            ytix,
            ztix,
        ):
            nfr = nF
            if progress is not None:
                progress.set_name("write refs")
                progress.set_max_advancement(len(refIndexes))
            for ref_index in refIndexes:
                int_rf = int(ref_index)
                test_val = 0
                if int_rf == projnum:
                    refUrl = refUrls[ref_index]
                    if ignore(os.path.basename(refUrl.file_path())):
                        _logger.info("ignore " + refUrl.file_path())
                        continue
                    data, header = read_url(refUrl)
                    dataDataset[nfr, :, :] = data + test_val
                    keysDataset[nfr] = ImageKey.FLAT_FIELD.value
                    keysCDataset[nfr] = ImageKey.FLAT_FIELD.value
                    if file_keys.motor_pos_key in header:
                        str_mot_val = header[file_keys.motor_pos_key].split(" ")
                        if raix == -1:
                            rotationDataset[nfr] = 0.0
                        else:
                            rotationDataset[nfr] = float(str_mot_val[raix])
                        if xtix == -1:
                            xDataset[nfr] = 0.0
                        else:
                            xDataset[nfr] = float(str_mot_val[xtix])
                        if ytix == -1:
                            yDataset[nfr] = 0.0
                        else:
                            yDataset[nfr] = float(str_mot_val[ytix])
                        if ztix == -1:
                            zDataset[nfr] = 0.0
                        else:
                            zDataset[nfr] = float(str_mot_val[ztix])

                    nfr += 1
                    if progress is not None:
                        progress.increase_advancement(i=1)
            return nfr

        # projections
        import datetime

        proj_indexes = sorted(proj_urls.keys())
        if progress is not None:
            progress.set_name("write projections")
            progress.set_max_advancement(len(proj_indexes))
        nproj = 0
        iref_pj = 0

        for proj_index in proj_indexes:
            proj_url = proj_urls[proj_index]
            if ignore(os.path.basename(proj_url.file_path())):
                _logger.info("ignore " + proj_url.file_path())
                continue

            # store refs if the ref serial number is = projection number
            if iref_pj < len(ref_projs) and ref_projs[iref_pj] == nproj:
                nf = store_refs(
                    ref_indexes,
                    scan.tomo_n,
                    ref_projs[iref_pj],
                    refs_urls,
                    nf,
                    data_dataset,
                    keys_dataset,
                    keys_control_dataset,
                    x_dataset,
                    y_dataset,
                    z_dataset,
                    rotation_dataset,
                    rot_angle_index,
                    x_trans_index,
                    y_trans_index,
                    z_trans_index,
                )
                iref_pj += 1
            data, header = read_url(proj_url)

            data_dataset[nf, :, :] = data
            keys_dataset[nf] = ImageKey.PROJECTION.value
            keys_control_dataset[nf] = ImageKey.PROJECTION.value
            if nproj >= scan.tomo_n:
                keys_control_dataset[nf] = ImageKey.ALIGNMENT.value

            if file_keys.motor_pos_key in header:
                str_mot_val = header[file_keys.motor_pos_key].split(" ")

                # continuous scan - rot angle is unknown. Compute it
                if compute_rotangle is True and nproj < scan.tomo_n:
                    rotation_dataset[nf] = nproj * proj_angle
                else:
                    if rot_angle_index == -1:
                        rotation_dataset[nf] = 0.0
                    else:
                        rotation_dataset[nf] = float(str_mot_val[rot_angle_index])

                if x_trans_index == -1:
                    x_dataset[nf] = 0.0
                else:
                    x_dataset[nf] = float(str_mot_val[x_trans_index])
                if y_trans_index == -1:
                    y_dataset[nf] = 0.0
                else:
                    y_dataset[nf] = float(str_mot_val[y_trans_index])
                if z_trans_index == -1:
                    z_dataset[nf] = 0.0
                else:
                    z_dataset[nf] = float(str_mot_val[z_trans_index])

            nf += 1
            nproj += 1

            if progress is not None:
                progress.increase_advancement(i=1)

        # store last flat if any remaining in the list
        if iref_pj < len(ref_projs):
            nf = store_refs(
                ref_indexes,
                scan.tomo_n,
                ref_projs[iref_pj],
                refs_urls,
                nf,
                data_dataset,
                keys_dataset,
                keys_control_dataset,
                x_dataset,
                y_dataset,
                z_dataset,
                rotation_dataset,
                rot_angle_index,
                x_trans_index,
                y_trans_index,
                z_trans_index,
            )

        # we can add some more NeXus look and feel
        h5d["/entry"].attrs["NX_class"] = u"NXentry"
        h5d["/entry"].attrs["definition"] = u"NXtomo"
        h5d["/entry"].attrs["version"] = converter_version()
        h5d["/entry/instrument"].attrs["NX_class"] = u"NXinstrument"
        h5d["/entry/instrument/detector"].attrs["NX_class"] = u"NXdetector"
        h5d["/entry/instrument/detector/data"].attrs["interpretation"] = u"image"
        h5d["/entry/sample"].attrs["NX_class"] = u"NXsample"
        h5d["/entry/definition"] = "NXtomo"

        h5d.flush()

    try:
        create_nx_data_group(
            file_path=output_file, entry_path="entry", axis_scale=["linear", "linear"]
        )
    except Exception as e:
        _logger.error("Fail to create NXdata group. Reason is {}".format(str(e)))

    # create beam group at root for compatibility
    try:
        link_nxbeam_to_root(file_path=output_file, entry_path="entry")
    except Exception as e:
        pass

    return fileout_h5, "entry"
