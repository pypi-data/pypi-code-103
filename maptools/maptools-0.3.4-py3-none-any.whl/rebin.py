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
import scipy.signal
from maptools.util import read, write


# Get the logger
logger = logging.getLogger(__name__)


# def array_rebin(data, shape):
#    """
#    Rebin a multidimensional array
#
#    Args:
#        data (array): The input array
#        shape (tuple): The new shape
#
#    """
#
#    # Ensure dimensions are consistent
#    assert data.ndim == len(shape)
#    assert data.shape[0] % shape[0] == 0
#    assert data.shape[1] % shape[1] == 0
#    assert data.shape[2] % shape[2] == 0
#
#    # Get pairs of (shape, bin factor) for each dimension
#    factors = numpy.array([(d, c // d) for d, c in zip(shape, data.shape)])
#
#    # Rebin the array
#    data = data.reshape(factors.flatten())
#    for i in range(len(shape)):
#        data = data.sum(-1 * (i + 1))
#    return data
def array_rebin(data, shape):
    """
    Rebin a multidimensional array

    Args:
        data (array): The input array
        shape (tuple): The new shape

    """
    # Get pairs of (shape, bin factor) for each dimension
    factors = numpy.array([(d, c // d) for d, c in zip(shape, data.shape)])

    # Rebin the array
    for i in range(len(factors)):
        data = scipy.signal.decimate(data, factors[i][1], axis=i)
    # data = data.reshape(factors.flatten())
    # for i in range(len(shape)):
    #     data = data.sum(-1 * (i + 1))
    return data


def mapfile_rebin(input_map_filename, output_map_filename, shape=None):
    """
    Rebin the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        shape (tuple): The new shape of the map

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the data
    data = infile.data

    # Get the subset of data
    logger.info("Resampling map from shape %s to %s" % (data.shape, tuple(shape)))
    data = array_rebin(data, shape)

    # Write the output file
    outfile = write(output_map_filename, data, infile=infile)

    # Update the voxel size
    outfile.voxel_size = (
        outfile.voxel_size["z"] * infile.data.shape[0] // shape[0],
        outfile.voxel_size["y"] * infile.data.shape[1] // shape[1],
        outfile.voxel_size["x"] * infile.data.shape[2] // shape[2],
    )


def rebin(*args, **kwargs):
    """
    Rebin the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_rebin
    else:
        func = array_rebin
    return func(*args, **kwargs)
