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


def fft(input_map_filename, output_map_filename, mode=None, shift=True, normalize=True):
    """
    Compute the FFT of the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        mode (str): The component to output
        shift (bool): Shift the fourier components
        normalize (bool): Normalize before computing FFT

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the subset of data
    logger.info("Computing FFT (%s)" % mode)

    # The data
    data = infile.data

    # Normalize if necessary
    if normalize:
        data = (data - numpy.mean(data)) / numpy.std(data)

    # Compute FFT
    data = {
        "real": lambda x: numpy.real(x),
        "imaginary": lambda x: numpy.imag(x),
        "amplitude": lambda x: numpy.abs(x),
        "phase": lambda x: numpy.angle(x),
        "power": lambda x: numpy.abs(x) ** 2,
    }[mode](numpy.fft.fftn(data).astype("complex64"))

    # Shift if necessary
    if shift:
        data = numpy.fft.fftshift(data)

    # Write the output file
    write(output_map_filename, data, infile=infile)
