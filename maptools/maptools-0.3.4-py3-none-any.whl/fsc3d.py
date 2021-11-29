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
import scipy.ndimage
from maptools.util import read, write, read_axis_order
from maptools.reorder import reorder


# Get the logger
logger = logging.getLogger(__name__)


def array_fsc3d(
    data1, data2, kernel=9, resolution=None, voxel_size=(1, 1, 1), **kwargs
):
    """
    Compute the local FSC of the map

    Args:
        data1 (array): The input map 1
        data2 (array): The input map 2
        kernel (int): The kernel size
        resolution (float): The resolution limit

    Returns:
        array: The local FSC map

    """

    # Get the subset of data
    logger.info("Computing local FSC")

    # Normalize the data
    data1 = (data1 - numpy.mean(data1)) / numpy.std(data1)
    data2 = (data2 - numpy.mean(data2)) / numpy.std(data2)

    # Compute the FFT of the data
    X = numpy.fft.fftshift(numpy.fft.fftn(data1))
    Y = numpy.fft.fftshift(numpy.fft.fftn(data2))

    # Compute local variance and covariance
    varX = scipy.ndimage.uniform_filter(numpy.abs(X) ** 2, size=kernel, mode="nearest")
    varY = scipy.ndimage.uniform_filter(numpy.abs(Y) ** 2, size=kernel, mode="nearest")
    covXY = scipy.ndimage.uniform_filter(
        numpy.real(X * numpy.conj(Y)), size=kernel, mode="nearest"
    )

    # Compute the FSC
    fsc = numpy.zeros(covXY.shape)
    tiny = 1e-5
    mask = (varX > tiny) & (varY > tiny)
    fsc[mask] = covXY[mask] / (numpy.sqrt(varX[mask]) * numpy.sqrt(varY[mask]))

    # Create a resolution mask
    if resolution is not None:
        shape = fsc.shape
        Z, Y, X = numpy.mgrid[0 : shape[0], 0 : shape[1], 0 : shape[2]]
        Z = (1.0 / voxel_size["z"]) * (Z - shape[0] // 2) / shape[0]
        Y = (1.0 / voxel_size["y"]) * (Y - shape[1] // 2) / shape[1]
        X = (1.0 / voxel_size["x"]) * (X - shape[2] // 2) / shape[2]
        R = numpy.sqrt(X ** 2 + Y ** 2 + Z ** 2)
        mask = R < 1.0 / resolution
        fsc *= mask

    # Print some output
    logger.info("Min CC = %f, Max CC = %f" % (fsc.min(), fsc.max()))

    # Return the fsc
    return fsc


def mapfile_fsc3d(
    input_map_filename1,
    input_map_filename2,
    output_map_filename=None,
    kernel=9,
    resolution=None,
):
    """
    Compute the local FSC of the map

    Args:
        input_map_filename1 (str): The input map filename
        input_map_filename2 (str): The input map filename
        output_map_filename (str): The output map filename
        kernel (int): The kernel size
        resolution (float): The resolution limit

    """

    # Open the input files
    infile1 = read(input_map_filename1)
    infile2 = read(input_map_filename2)

    # Get the data
    data1 = infile1.data
    data2 = infile2.data

    # Reorder input arrays
    data1 = reorder(data1, read_axis_order(infile1), (0, 1, 2))
    data2 = reorder(data2, read_axis_order(infile2), (0, 1, 2))

    # Compute the local FSC
    fsc = fsc3d(
        data1,
        data2,
        kernel=kernel,
        resolution=resolution,
        voxel_size=infile1.voxel_size,
    )

    # Reorder output array
    fsc = reorder(fsc, (0, 1, 2), read_axis_order(infile1))

    # Write the output file
    write(output_map_filename, fsc.astype("float32"), infile=infile1)


def fsc3d(*args, **kwargs):
    """
    Compute the local FSC of the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename1" in kwargs:
        func = mapfile_fsc3d
    else:
        func = array_fsc3d
    return func(*args, **kwargs)
