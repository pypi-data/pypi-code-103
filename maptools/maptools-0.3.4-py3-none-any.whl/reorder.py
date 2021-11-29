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
from maptools.util import read, write, read_axis_order, write_axis_order


# Get the logger
logger = logging.getLogger(__name__)


def array_reorder(data, original_order, new_order):
    """
    Reorder the data axes

    Args
        data (array): The data array
        original_order (tuple): The original order
        new_order (tuple): The new order

    Returns:
        The reordered data

    """

    def swap(x, a, b):
        x[a], x[b] = x[b], x[a]
        return x

    # Convert to list
    original_order = list(original_order)

    # Reorder the axes
    index = original_order.index(new_order[0])
    if index != 0:
        logger.info("Swapping axis %d with %d" % (0, index))
        data = numpy.swapaxes(data, 0, index)
        original_order = swap(original_order, 0, index)
    index = original_order.index(new_order[1])
    if index != 1:
        logger.info("Swapping axis %d with %d" % (1, index))
        data = numpy.swapaxes(data, 1, index)
        original_order = swap(original_order, 1, index)
    assert tuple(original_order) == tuple(new_order)

    # Return the reordered array
    return data


def mapfile_reorder(input_map_filename, output_map_filename, axis_order=None):
    """
    Reorder the data axes

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        axis_order (list): The axis order

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the axis order
    original_order = read_axis_order(infile)
    assert tuple(sorted(axis_order)) == (0, 1, 2)

    # Reorder the axes
    data = array_reorder(infile.data, original_order, axis_order)

    # Write the output file
    outfile = write(output_map_filename, data, infile=infile)
    write_axis_order(outfile, axis_order)
    outfile.update_header_stats()


def reorder(*args, **kwargs):
    """
    Reorder the data axes

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_reorder
    else:
        func = array_reorder
    return func(*args, **kwargs)
