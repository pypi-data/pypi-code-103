#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import logging
import mrcfile
import numpy


# Get the logger
logger = logging.getLogger(__name__)


def read(filename, mode="r"):
    """
    Read the input map file

    Args:
        filename (str): The map filename

    Return
        object: The map file

    """
    logger.info("Reading %s" % filename)
    return mrcfile.mmap(filename, mode=mode)


def write(filename, data, infile=None):
    """
    Write the output map file

    Args:
        filename (str): The map filename
        data (object): The data to write
        infile (object): The input file

    """
    logger.info("Writing %s" % filename)
    if data.dtype == numpy.float64:
        data = data.astype("float32")
    outfile = mrcfile.new(filename, overwrite=True)
    outfile.set_data(data)
    if infile is not None:
        outfile.voxel_size = infile.voxel_size
        outfile.header["mapc"] = infile.header["mapc"]
        outfile.header["mapr"] = infile.header["mapr"]
        outfile.header["maps"] = infile.header["maps"]
        outfile.header["origin"] = infile.header["origin"]
    outfile.update_header_stats()
    return outfile


def read_axis_order(infile):
    """
    Get the axis order (in C order)

    Args:
        infile (object): the input file handle

    Returns:
        tuple: The axis order

    """

    # Axes are written into file in order
    # 1 = X
    # 2 = Y
    # 3 = Y
    #
    # Out order here is C order with
    # 0 = Z
    # 1 = Y
    # 2 = X
    lookup_fwd = {1: 2, 2: 1, 3: 0}

    # Get the axis order
    order = [
        lookup_fwd[int(infile.header["maps"])],
        lookup_fwd[int(infile.header["mapr"])],
        lookup_fwd[int(infile.header["mapc"])],
    ]
    assert tuple(sorted(order)) == (0, 1, 2)
    return order


def write_axis_order(outfile, order):
    """
    Set the axis order (in C order)

    Args:
        outfile (object): the output file handle
        order (tuple): The axis order

    """

    # Axes are written into file in order
    # 1 = X
    # 2 = Y
    # 3 = Y
    #
    # Out order here is C order with
    # 0 = Z
    # 1 = Y
    # 2 = X
    lookup_rev = {2: 1, 1: 2, 0: 3}

    # Write the axis order
    outfile.header["maps"] = lookup_rev[order[0]]
    outfile.header["mapr"] = lookup_rev[order[1]]
    outfile.header["mapc"] = lookup_rev[order[2]]
