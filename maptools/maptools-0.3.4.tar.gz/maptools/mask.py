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
from maptools.util import read, write, read_axis_order
from maptools.reorder import reorder


# Get the logger
logger = logging.getLogger(__name__)


def array_mask(data, mask, value=0, zero=True, fourier_space=False, shift=False):
    """
    Mask the map

    Args:
        data (array): The map
        mask (array): The mask
        space (str): Apply in real space or fourier space
        shift (bool): Shift the mask

    Returns:
        array: The masked map

    """

    # Apply mask
    if shift:
        logger.info("Shifting mask")
        mask = numpy.fft.fftshift(mask)
    if not fourier_space:
        logger.info("Applying mask in real space")
        data = data * mask
        # mask = mask > 0
        # data = data * mask + (~mask) * value
        # if zero:
        #     masked_data = data[mask]
        #     data[mask] = masked_data - numpy.min(masked_data) + value
    else:
        logger.info("Applying mask in Fourier space")
        data = numpy.real(numpy.fft.ifftn(numpy.fft.fftn(data) * mask))

    # Return the masked map
    return data


def mapfile_mask(
    input_map_filename,
    output_map_filename,
    input_mask_filename=None,
    fourier_space=False,
    shift=False,
):
    """
    Mask the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        input_mask_filename (str): The mask filename
        space (str): Apply in real space or fourier space
        shift (bool): Shift the mask

    """

    # Open the input file
    infile = read(input_map_filename)

    # Open the mask file
    maskfile = read(input_mask_filename)

    # Apply the mask
    data = infile.data
    mask = maskfile.data

    # Reorder the maskfile axes to match the data
    mask = reorder(mask, read_axis_order(maskfile), read_axis_order(infile))

    # Apply the mask
    data = array_mask(data, mask, fourier_space=fourier_space, shift=shift)

    # Write the output file
    write(output_map_filename, data.astype("float32"), infile=infile)


def mask(*args, **kwargs):
    """
    Mask the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_mask
    else:
        func = array_mask
    return func(*args, **kwargs)
