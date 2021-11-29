#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import logging
import numpy
from math import sqrt, log
from maptools.util import read, write


# Get the logger
logger = logging.getLogger(__name__)


def array_filter(
    data,
    filter_type="lowpass",
    filter_shape="gaussian",
    resolution=None,
    voxel_size=(1, 1, 1),
):
    # Check input resolution
    if type(resolution) == int or type(resolution) == float:
        resolution = [resolution]
    resolution = list(sorted(resolution))

    # Compute the FFT of the input data
    fdata = numpy.fft.fftn(data)

    # Compute the radius in Fourier space
    z, y, x = numpy.mgrid[0 : fdata.shape[0], 0 : fdata.shape[1], 0 : fdata.shape[2]]
    z = (1 / voxel_size[0]) * (z - fdata.shape[0] // 2) / fdata.shape[0]
    y = (1 / voxel_size[1]) * (y - fdata.shape[1] // 2) / fdata.shape[1]
    x = (1 / voxel_size[2]) * (x - fdata.shape[2] // 2) / fdata.shape[2]
    r = numpy.sqrt(x ** 2 + y ** 2 + z ** 2)
    r = numpy.fft.fftshift(r)

    # Create the filter mask
    if filter_type == "lowpass":

        # Create the low pass filter
        assert len(resolution) == 1
        resolution = resolution[0]
        if filter_shape == "gaussian":
            sigma = 1.0 / (sqrt(2 * log(2)) * resolution)
            mask = numpy.exp(-0.5 * (r / sigma) ** 2)
        elif filter_shape == "square":
            mask = r < (1 / resolution)

    elif filter_type == "highpass":

        # Create the high pass filter
        assert len(resolution) == 1
        resolution = resolution[0]
        assert filter_shape == "square"
        mask = r >= (1 / resolution)

    elif filter_type == "bandpass":

        # Create the band pass filter
        assert len(resolution) == 2
        assert resolution[1] > resolution[0]
        assert filter_shape == "square"
        mask = (r >= (1 / resolution[1])) & (r < (1 / resolution[0]))

    elif filter_type == "bandstop":

        # Create the band stop filter
        assert len(resolution) == 2
        assert resolution[1] > resolution[0]
        assert filter_shape == "square"
        mask = (r < (1 / resolution[1])) & (r >= (1 / resolution[0]))

    # Apply the filter
    logger.info(
        "Applying %s (%s) filter with resolution %sA"
        % (filter_type, filter_shape, resolution)
    )
    data = numpy.real(numpy.fft.ifftn(fdata * mask)).astype("float32")

    # Return the data
    return data


def mapfile_filter(
    input_map_filename,
    output_map_filename,
    filter_type="lowpass",
    filter_shape="gaussian",
    resolution=None,
):
    """
    Filter the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        filter_type (str): The filter type
        filter_shape (str): The filter shape
        resolution (list): The resolution

    """

    # Check the input
    assert filter_type in ["lowpass", "highpass", "bandpass", "bandstop"]
    assert filter_shape in ["square", "gaussian"]

    # Open the input file
    infile = read(input_map_filename)

    # Get the voxel size
    voxel_size = (
        infile.voxel_size["z"],
        infile.voxel_size["y"],
        infile.voxel_size["x"],
    )

    # Filter the data
    data = array_filter(
        infile.data,
        filter_type=filter_type,
        filter_shape=filter_shape,
        resolution=resolution,
        voxel_size=voxel_size,
    )

    # Write the output file
    write(output_map_filename, data, infile=infile)


def filter(*args, **kwargs):
    """
    Compute the local FSC of the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_filter
    else:
        func = array_filter
    return func(*args, **kwargs)
