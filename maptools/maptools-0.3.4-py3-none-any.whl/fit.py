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
from maptools.util import read


# Get the logger
logger = logging.getLogger(__name__)


def fit(
    input_map_filename,
    input_pdb_filename,
    output_pdb_filename=None,
    resolution=1,
    ncycle=10,
    mode="rigid_body",
    log_filename="fit.log",
):
    """
    Compute the CC between two maps

    Args:
        input_map_filename (str): The input map filename
        input_pdb_filename (str): The input pdb filename
        output_filename (str): The output pdb filename
        resolution (float): The resolution
        ncycle (float): The number of cycles
        mode (str): The refinement mode
        log_filename (str): The log filename

    """

    # Read the grid from the map
    input_map_file = read(input_map_filename)
    cell = tuple(input_map_file.header.cella.tolist())

    # Get a working directory
    wd = tempfile.mkdtemp()

    # Open log
    with open(log_filename, "w") as stdout:

        # Call refmac to convert map to mtz
        maptools.external.map2mtz(
            mapin=os.path.abspath(input_map_filename),
            hklout="input.mtz",
            resolution=resolution,
            wd=wd,
            stdout=stdout,
            param_file="map2mtz.dat",
            command_file="map2mtz.sh",
        )

        # Setup the pdb file
        maptools.external.pdbset(
            xyzin=os.path.abspath(input_pdb_filename),
            xyzout="pdbset.pdb",
            cell=cell,
            stdout=stdout,
            wd=wd,
            param_file="pdbset.dat",
            command_file="pdbset.sh",
        )

        # Setup the pdb file
        maptools.external.refine(
            xyzin="pdbset.pdb",
            hklin="input.mtz",
            xyzout=os.path.abspath(output_pdb_filename),
            hklout="refined.mtz",
            mode=mode,
            ncycle=ncycle,
            resolution=resolution,
            stdout=stdout,
            wd=wd,
            param_file="refmac.dat",
            command_file="refmac.sh",
        )
