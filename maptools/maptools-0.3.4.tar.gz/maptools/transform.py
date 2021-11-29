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
import scipy.spatial.transform
from math import pi
from maptools.util import read, write, read_axis_order


# Get the logger
logger = logging.getLogger(__name__)


def array_transform(
    data,
    axis_order=(0, 1, 2),
    offset=None,
    rotation=(0, 0, 0),
    translation=(0, 0, 0),
    deg=False,
):
    """
    Transform the map

    Args:
        data (array): The data to transform
        offset = (array): The offset to rotate about
        rotation (array): The rotation vector
        translation (array): The translation vector
        deg (bool): Is the rotation in degrees

    Returns:
        array: The transformed data

    """
    assert tuple(sorted(axis_order)) == (0, 1, 2)

    # Set the offset
    if offset is None:
        offset = numpy.array(data.shape) / 2
    else:
        offset = numpy.array(offset)
        offset = offset[axis_order]

    # Reorder input vectors
    translation = numpy.array(translation)[axis_order]
    rotation = numpy.array(rotation)[axis_order]

    # If the rotation is in degrees transform
    if deg:
        rotation = numpy.array(rotation) * pi / 180

    # Create the rotation matrix
    rotation = scipy.spatial.transform.Rotation.from_rotvec(rotation).as_matrix()
    O = numpy.diag((1.0, 1.0, 1.0, 1.0))
    T = numpy.diag((1.0, 1.0, 1.0, 1.0))
    T[0:3, 0:3] = rotation
    T[0:3, 3] = translation
    O[0:3, 3] = offset
    matrix = numpy.matmul(O, numpy.matmul(T, numpy.linalg.inv(O)))

    # Do the transformation
    logger.info("Performing transformation")
    logger.info("matrix=")
    logger.info(matrix)
    data = scipy.ndimage.affine_transform(data, numpy.linalg.inv(matrix))

    # Return the transformed data
    return data


def mapfile_transform(
    input_map_filename,
    output_map_filename,
    offset=None,
    rotation=(0, 0, 0),
    translation=(0, 0, 0),
    deg=False,
):
    """
    Transform the map

    Args:
        input_map_filename (str): The input map filename
        output_map_filename (str): The output map filename
        offset = (array): The offset to rotate about
        rotation (array): The rotation vector
        translation (array): The translation vector
        deg (bool): Is the rotation in degrees

    """

    # Open the input file
    infile = read(input_map_filename)

    # Get the axis order
    axis_order = read_axis_order(infile)

    # Get data
    data = infile.data

    # Do the transform
    data = array_transform(
        data,
        axis_order=axis_order,
        offset=offset,
        rotation=rotation,
        translation=translation,
        deg=deg,
    )

    # Write the output file
    write(output_map_filename, data, infile=infile)


def transform(*args, **kwargs):
    """
    Transform the data

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename" in kwargs:
        func = mapfile_transform
    else:
        func = array_transform
    return func(*args, **kwargs)
