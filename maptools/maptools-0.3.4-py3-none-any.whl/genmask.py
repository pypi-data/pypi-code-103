#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import gemmi
import logging
import numpy
import scipy.ndimage.morphology
from maptools.util import write


# Get the logger
logger = logging.getLogger(__name__)


def genmask(
    input_pdb_filename=None,
    output_mask_filename=None,
    atom_radius=5,
    border=0,
    shape=None,
    voxel_size=1,
    sigma=0,
):
    """
    Generate the mask

    Args:
        input_pdb_filename (str): The input pdb filename
        output_mask_filename (str): The output map filename
        atom_radius (float): The radius around the atoms
        border (int): The border of pixels
        shape (tuple): The shape of the output map
        voxel_size (float): The voxel size of the output map
        sigma (float): Soften the mask with a Gaussian edge

    """

    # Create the mask
    mask = numpy.ones(shape, dtype="bool")

    # Add a border
    mask[:border, :, :] = 0
    mask[-border - 1 :, :, :] = 0
    mask[:, :border, :] = 0
    mask[:, -border - 1 :, :] = 0
    mask[:, :, :border] = 0
    mask[:, :, -border - 1 :] = 0

    # Add atom mask
    if input_pdb_filename is not None:

        # Read the structure
        structure = gemmi.read_structure(input_pdb_filename)

        # Get the coordinates
        coords = numpy.array(
            [
                (atom.pos.z, atom.pos.y, atom.pos.x)
                for model in structure
                for chain in model
                for residue in chain
                for atom in residue
            ]
        ).T

        # Print some infor
        logger.info("Min / Max X: %f / %f" % (coords[2].min(), coords[2].max()))
        logger.info("Min / Max Y: %f / %f" % (coords[1].min(), coords[1].max()))
        logger.info("Min / Max Z: %f / %f" % (coords[0].min(), coords[0].max()))

        # Convert to indices
        index = numpy.floor(coords / voxel_size).astype("int32")
        atoms = numpy.ones(shape)
        atoms[index[0], index[1], index[2]] = 0

        # Compute distance and update mask
        distance = scipy.ndimage.morphology.distance_transform_edt(
            atoms, sampling=voxel_size
        )
        mask = mask & (distance <= atom_radius)

    # Soften the mask
    if sigma > 0:
        logger.info("Soften mask edge with sigma = %f" % sigma)
        distance = scipy.ndimage.morphology.distance_transform_edt(
            ~mask, sampling=voxel_size
        )
        mask = numpy.exp(-0.5 * distance ** 2 / sigma ** 2)

    # Write the output file
    outfile = write(output_mask_filename, mask.astype("float32"))
    outfile.voxel_size = voxel_size
