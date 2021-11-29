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


def array_threshold(data, threshold=0, normalize=False, zero=True):
    """
    Threshold the map

    Args:
        data (array): The input data
        threshold (float): The threshold value
        normalize (bool): Normalize the map before thresholding
        zero (bool): Shift the data to zero

    Returns:
        array: The thresholded array

    """

    # Apply the threshold
    logger.info("Apply threshold %f" % threshold)
    if normalize:
        data = (data - numpy.mean(data)) / numpy.std(data)
    mask = data >= threshold
    data[~mask] = threshold
    if zero:
        data -= threshold

    # Return the data
    return data, mask


def mapfile_threshold(
    input_map_filename,
    output_map_filename,
    output_mask_filename=None,
    threshold=0,
    normalize=False,
    zero=True,
):
    """
    Threshold the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        threshold (float): The threshold value
        normalize (bool): Normalize the map before thresholding
        zero (bool): Shift the data to zero

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get data
    data = infile.data.copy()

    # Apply the threshold
    data, mask = array_threshold(
        data, threshold=threshold, normalize=normalize, zero=zero
    )

    # Write the output file
    write(output_map_filename, data, infile=infile)

    # Write the mask
    if output_mask_filename:
        write(output_mask_filename, mask.astype("uint8"), infile=infile)


def threshold(*args, **kwargs):
    """
    Threshold the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_threshold
    else:
        func = array_threshold
    return func(*args, **kwargs)
