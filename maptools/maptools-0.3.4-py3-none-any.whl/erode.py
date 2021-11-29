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
import scipy.ndimage.morphology
from maptools.util import read, write


# Get the logger
logger = logging.getLogger(__name__)


def array_erode(data, kernel=3, num_iter=1):
    """
    Dilate the map

    Args:
        data (array): The array
        kernel (int): The kernel size
        num_iter (int): The number of iterations

    """
    # Generate a mask
    z, y, x = numpy.mgrid[0:kernel, 0:kernel, 0:kernel]
    z = z - kernel // 2
    y = y - kernel // 2
    x = x - kernel // 2
    r = numpy.sqrt(x ** 2 + y ** 2 + z ** 2)
    mask = r <= kernel // 2

    # Do the dilation
    return scipy.ndimage.morphology.binary_dilation(data, mask, num_iter)


def mapfile_erode(input_map_filename, output_map_filename, kernel=3, num_iter=1):
    """
    Dilate the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        kernel (tuple): The kernel size
        num_iter (int): The number of iterations

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the subset of data
    logger.info("Dilating map")
    data = array_erode(infile.data, kernel=kernel, num_iter=num_iter)

    # Write the output file
    write(output_map_filename, data.astype("uint8"), infile=infile)


def erode(*args, **kwargs):
    """
    Dilate the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_erode
    else:
        func = array_erode
    return func(*args, **kwargs)
