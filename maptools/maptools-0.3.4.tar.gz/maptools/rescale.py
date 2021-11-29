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
from maptools.util import read, write


# Get the logger
logger = logging.getLogger(__name__)


def array_rescale(
    data, mean=None, sdev=None, vmin=None, vmax=None, scale=None, offset=None
):
    """
    Rescale the map

    Args:
        data (array): The input map
        mean (float): The desired mean value
        sdev (float): The desired sdev value
        vmin (float): The desired min value
        vmax (float): The desired max value
        scale (float): The scale
        offset (float): The offset

    Returns:
        array: The output map

    """

    # Normalize by mean and standard deviation
    if mean is not None or sdev is not None:
        original_mean = numpy.mean(data)
        original_sdev = numpy.std(data)
        if mean is None:
            mean = original_mean
        if sdev is None:
            sdev = original_sdev
        scale = sdev / original_sdev
        offset = mean - original_mean * scale

    # Normalize by min and max
    if vmin is not None or vmax is not None:
        original_min = numpy.min(data)
        original_max = numpy.max(data)
        if vmin is None:
            vmin = original_mean
        if vmax is None:
            vmax = original_sdev
        scale = (vmax - vmin) / (original_max - original_min)
        offset = vmin - original_min * scale

    # If the scale and offset are set
    if scale is None:
        scale = 1
    if offset is None:
        offset = 0

    # Get the subset of data
    logger.info("Rescaling map with scale = %g and offset = %g" % (scale, offset))
    data = data * scale + offset
    logger.info(
        "Data min = %g, max = %g, mean = %g, sdev = %g"
        % (data.min(), data.max(), numpy.mean(data), numpy.std(data))
    )

    # Return the rescaled map
    return data


def mapfile_rescale(
    input_map_filename,
    output_map_filename,
    mean=None,
    sdev=None,
    vmin=None,
    vmax=None,
    scale=None,
    offset=None,
):
    """
    Rescale the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        mean (float): The desired mean value
        sdev (float): The desired sdev value
        vmin (float): The desired min value
        vmax (float): The desired max value
        scale (float): The scale
        offset (float): The offset

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the data
    data = infile.data

    # Rescale the map
    data = array_rescale(
        data, mean=mean, sdev=sdev, vmin=vmin, vmax=vmax, scale=scale, offset=offset
    )

    # Write the output file
    write(output_map_filename, data, infile=infile)


def rescale(*args, **kwargs):
    """
    Rescale the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_rescale
    else:
        func = array_rescale
    return func(*args, **kwargs)
