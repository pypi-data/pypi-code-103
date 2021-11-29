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
import subprocess


logger = logging.getLogger(__name__)


def is_ccp4_available():
    """
    Check if CCP4 is available

    """
    return os.environ.get("CCP4", None) not in [None, ""]


class cd:
    """
    Context manager for changing the current working directory

    """

    def __init__(self, new_path):
        """
        Init the context manager

        """
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        """
        Change directory

        """
        self.old_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        """
        Change back

        """
        os.chdir(self.old_path)


def call(command, stdin=None, stdout=None):
    """
    Call an external command

    """

    # Call the process
    process = subprocess.Popen(
        command, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    # Process the stdout
    for line in process.stdout:
        line = line.decode("utf-8")
        logger.info(line.strip("\n"))
        if stdout is not None:
            stdout.write(line)
    process.wait()

    # Check the error code
    if process.returncode != 0:
        raise RuntimeError("Command returned with error %d" % process.returncode)


def call_ccp4(
    command, params=None, stdout=None, wd=None, param_file=None, command_file=None
):
    """
    Call a CCP4 style program

    """

    # Check if CCP4 is available
    if not is_ccp4_available():
        raise RuntimeError("CCP4 is not available")

    # Create the working directory
    if wd is None:
        wd = "."

    # Make the directory
    if not os.path.exists(wd):
        os.mkdir(wd)

    # Change into a temporary directory
    with cd(os.path.expanduser(wd)):

        # Set the parameter file
        if param_file is None:
            param_file = "params.dat"

        # Set the command file
        if command_file is None:
            command_file = "command.dat"

        # Check the parameters
        if params is None:
            params = []

        # Construct the parameter file
        with open(param_file, "w") as outfile:
            outfile.write("\n".join(params))

        # Write the command file
        with open(command_file, "w") as outfile:
            outfile.write("cat %s | %s" % (param_file, " ".join(command)))

        # Call the command
        with open(param_file, "r") as stdin:
            call(command, stdin=stdin, stdout=stdout)


def call_fft(
    hklin=None,
    mapout=None,
    params=None,
    stdout=None,
    wd=None,
    param_file=None,
    command_file=None,
):
    """
    Call fft

    """

    # Construct the command
    command = ["fft"]
    if hklin is not None:
        command.extend(["hklin", hklin])
    if mapout is not None:
        command.extend(["mapout", mapout])

    # Call the command
    call_ccp4(
        command,
        params,
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )


def call_pdbset(
    xyzin=None,
    xyzout=None,
    params=None,
    stdout=None,
    wd=None,
    param_file=None,
    command_file=None,
):
    """
    Call pdbset

    """

    # Construct the command
    command = ["pdbset"]
    if xyzin is not None:
        command.extend(["xyzin", xyzin])
    if xyzout is not None:
        command.extend(["xyzout", xyzout])

    # Call the command
    call_ccp4(
        command,
        params,
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )


def call_refmac5(
    hklin=None,
    xyzin=None,
    mapin=None,
    hklout=None,
    xyzout=None,
    params=None,
    stdout=None,
    wd=None,
    param_file=None,
    command_file=None,
):
    """
    Call REFMAC5

    """

    # Construct the command
    command = ["refmac5"]
    if hklin is not None:
        command.extend(["hklin", hklin])
    if xyzin is not None:
        command.extend(["xyzin", xyzin])
    if mapin is not None:
        command.extend(["mapin", mapin])
    if hklout is not None:
        command.extend(["hklout", hklout])
    if xyzout is not None:
        command.extend(["xyzout", xyzout])

    # Call the command
    call_ccp4(
        command,
        params,
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )


def pdbset(
    xyzin, xyzout, cell=None, wd=None, stdout=None, param_file=None, command_file=None
):
    """
    Use pdbset to set the cell

    """

    # Call pdbset
    call_pdbset(
        xyzin=xyzin,
        xyzout=xyzout,
        params=["cell %d %d %d 90 90 90" % tuple(cell), "end"],
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )

    # Check the output file exists
    if not os.path.isabs(xyzout):
        xyzout = os.path.join(wd, xyzout)
    assert os.path.exists(xyzout)


def pdb2mtz(
    xyzin,
    hklout,
    resolution=1,
    wd=None,
    stdout=None,
    param_file=None,
    command_file=None,
):
    """
    Use refmac to convert a pdb to an mtz

    """

    # Call refmac
    call_refmac5(
        xyzin=xyzin,
        xyzout="xyzout.pdb",
        hklout="hklout.mtz",
        params=[
            "mode sfcalc",
            "sfcalc cr2f",
            "source EM MB",
            "reso %f" % resolution,
            "sfcalc blur",
            "bfactor set 10",
            "end",
        ],
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )

    # Check the output file exists
    assert os.path.exists(os.path.join(wd, "sfcalc_from_crd.mtz"))

    # Move the file to the output
    if not os.path.isabs(hklout):
        hklout = os.path.join(wd, hklout)
    os.replace(os.path.join(wd, "sfcalc_from_crd.mtz"), hklout)


def mtz2map(
    hklin,
    mapout,
    grid=None,
    resolution=1,
    wd=None,
    stdout=None,
    param_file=None,
    command_file=None,
):
    """
    Use fft to convert an mtz to map file

    """

    # Convert using fft
    call_fft(
        hklin=hklin,
        mapout=mapout,
        params=[
            "labin F1=Fout0 PHI=Pout0",
            "grid %d %d %d" % tuple(grid),
            "reso %f" % resolution,
            "end",
        ],
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )

    # Check the output file exists
    if not os.path.isabs(mapout):
        mapout = os.path.join(wd, mapout)
    assert os.path.exists(mapout)


def map2mtz(
    mapin,
    hklout,
    resolution=1,
    wd=None,
    stdout=None,
    param_file=None,
    command_file=None,
):
    """
    Use refmac to convert a map to mtz file

    """

    # Call refmac to convert map to mtz
    call_refmac5(
        mapin=mapin,
        hklout=hklout,
        params=[
            "mode sfcalc",
            "source EM MB",
            "reso %f" % resolution,
            "sfcalc blur",
            "end",
        ],
        stdout=None,
        wd=wd,
    )

    # Check output file
    if not os.path.isabs(hklout):
        hklout = os.path.join(wd, hklout)
    assert os.path.exists(hklout)


def refine(
    hklin,
    xyzin,
    hklout,
    xyzout,
    mode="rigid",
    ncycle=10,
    resolution=1,
    wd=None,
    stdout=None,
    param_file=None,
    command_file=None,
):
    """
    Do the refinement with refmac

    """

    # Create the refmac parameters for rigid body or jelly body
    if mode == "rigid_body":
        params = [
            "labin FP=Fout0 PHIB=Pout0",
            "mode rigid_body",
            "make hydr no",
            "solvent no",
            "source EM MB",
            "rigidbody ncycle %d" % ncycle,
            "BFACtor SET 40.0",
            "reso %f" % resolution,
            "moni medi",
            "rigid auto all",
            "end",
        ]
    elif mode == "jelly_body":
        params = [
            "labin FP=Fout0 PHIB=Pout0",
            "make hydr no",
            "solvent no",
            "source EM MB",
            "ncycle %d" % ncycle,
            "ncsr local",
            "BFACtor SET 40.0",
            "reso %f" % resolution,
            "ridge dist sigma 0.01",
            "ridge dist dmax 4.2",
            "end",
        ]
    else:
        raise RuntimeError("Unknown mode: %s" % mode)

    # Do the refinement
    call_refmac5(
        xyzin=xyzin,
        hklin=hklin,
        xyzout=xyzout,
        hklout=hklout,
        params=params,
        stdout=stdout,
        wd=wd,
        param_file=param_file,
        command_file=command_file,
    )

    # Check output file
    if not os.path.isabs(hklout):
        hklout = os.path.join(wd, hklout)
    if not os.path.isabs(xyzout):
        xyzout = os.path.join(wd, xyzout)
    assert os.path.exists(hklout)
    assert os.path.exists(xyzout)
