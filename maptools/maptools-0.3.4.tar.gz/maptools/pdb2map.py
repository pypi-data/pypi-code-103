#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import logging
import os
import tempfile
import maptools.external


# Get the logger
logger = logging.getLogger(__name__)


def pdb2map(input_pdb_filename, output_map_filename=None, resolution=1, grid=None):
    """
    Compute the CC between two maps

    Args:
        input_pdb_filename (str): The input pdb filename
        output_map_filename (str): The output map filename
        resolution (float): The resolution

    """

    # Get a working directory
    wd = tempfile.mkdtemp()

    # Setup the pdb file
    maptools.external.pdbset(
        xyzin=os.path.abspath(input_pdb_filename),
        xyzout="pdbset.pdb",
        cell=tuple(grid),
        stdout=None,
        wd=wd,
        param_file="pdbset.dat",
        command_file="pdbset.sh",
    )

    # Generate an mtz file from a pdb file using refmac
    maptools.external.pdb2mtz(
        xyzin="pdbset.pdb",
        hklout="hklout.mtz",
        resolution=resolution,
        stdout=None,
        wd=wd,
        param_file="map2mtz.dat",
        command_file="map2mtz.sh",
    )

    # Convert the mtz file to an mrc file
    maptools.external.mtz2map(
        hklin="hklout.mtz",
        mapout=os.path.abspath(output_map_filename),
        grid=tuple(grid),
        resolution=resolution,
        stdout=None,
        wd=wd,
        param_file="map2mtz.dat",
        command_file="map2mtz.sh",
    )
