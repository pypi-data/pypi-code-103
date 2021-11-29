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


def array_cc(data1, data2=None, **kwargs):
    """
    Compute the CC between two maps

    Args:
        data1 (array): The input map 1
        data2 (array): The input map 2

    Returns:
        array: The CC

    """

    # Compute the Fourier transform of the data
    fdata1 = numpy.fft.fftn((data1 - numpy.mean(data1)) / numpy.std(data1))

    # Transform data2
    if data2 is not None:
        fdata2 = numpy.fft.fftn((data2 - numpy.mean(data2)) / numpy.std(data2))
    else:
        fdata2 = fdata1

    # Compute the CC
    cc = (
        numpy.fft.fftshift(numpy.real(numpy.fft.ifftn(fdata1 * numpy.conj(fdata2))))
        / fdata1.size
    )

    # Print some output
    logger.info("Min CC = %f, Max CC = %f" % (cc.min(), cc.max()))

    # Return the CC
    return cc


def mapfile_cc(input_map_filename1, input_map_filename2=None, output_map_filename=None):
    """
    Compute the CC between two maps

    Args:
        input_map_filename1 (str): The input map filename
        input_map_filename2 (str): The input map filename
        output_map_filename (str): The output cc filename

    """

    # Open the input file
    infile1 = read(input_map_filename1)

    # Get the data
    data1 = infile1.data
    if input_map_filename2 is not None:
        infile2 = read(input_map_filename2)
        data2 = infile2.data
        data2 = reorder(data2, read_axis_order(infile2), read_axis_order(infile1))
    else:
        data2 = None

    # Compute the cc
    cc = array_cc(data1, data2)

    # Write the output file
    write(output_map_filename, cc.astype("float32"), infile=infile1)


def cc(*args, **kwargs):
    """
    Compute the CC between two maps

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename1" in kwargs:
        func = mapfile_cc
    else:
        func = array_cc
    return func(*args, **kwargs)
