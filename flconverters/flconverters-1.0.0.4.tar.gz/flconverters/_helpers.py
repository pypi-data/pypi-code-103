"""Helper functions."""

import os
import errno
import chardet
from pathlib import Path

def _format_check(*args, fmtype):
    """Checks for variable/s type. Helper to _typecheck.

    Args:
        * `__input__` ([type]: any): Input variable.
        * `fmtype` ([type]: any): Type of variable to check.

    Raises:
        TypeError: When type of variable is != to `fmtype`
    """
    for n in args:
        a = type(n).__name__
        if not isinstance(n, fmtype):
            raise TypeError(f'{n} must be a string not a type {a}')

def typecheck(__object__):
    """Check whether object is a directory.

    Args:
        * `__object__` ([type]: str): Path of file/directory.

    Raises:
        [type]: `TypeError` if __object__ is not a string.

    Returns:
        [type]: `bool`: True if directory, False if not.
    """

    _format_check(__object__, fmtype = str)
    return os.path.isdir(__object__)

def outpath(dinput, flinput):
    """Generate output file path.

    Args:
        * `dinput` ([type]: `str`): Input directory.
        * `flinput` ([type]: `str`): Input file. Must not be the TextIOWrapper!!!

    Returns:
        [type]: `str`: Output path.
    """

    file_name = os.path.splitext(os.path.basename(flinput))[0]
    subdir = str(os.path.join(dinput, file_name))

    return subdir

def compatibility(__inpobj__, __compat__):
    """Check for file compatibility. 

    Removes elements from an object (`__inpobj__`) that don't contain substrings
    equal to any of the substring of another list (`__compat__`).

    Arg:
        * `__inpobj__` ([type]: `str`): input directory.

        * `__compt__` ([type]: `lst`): List of compatible file types.

    Raises:
        * `OSError`: when no compatible files are given.

    Returns:
        [type]: `lst`: a list containing elements that contain substrings equal to the elements of the `compat` list."""

    contents = os.listdir(__inpobj__)  # List dir contents.

    contents[:] = [fl for fl in contents if any(ext in fl for ext in __compat__)]   # Removes elements in directory contents that
                                                                                    # don't contain the compatible extensions.

    if not contents:
        raise OSError('No compatible files found')

    return list(contents)

def typencd(__inpobj__):
    """Find encoding type of file.

    Args:
        * `__inpobj__` ([type]: `str`): Input file.

    Returns:
        [type]: `str`: Type of encoding.
    """

    rawdata = open(__inpobj__, 'rb').read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']

    return str(charenc)

def _pathcheck(*args):
    """Check if input file or directory exists.

    Args:
        * `args` ([type]: `str`): input file or directory.

    Returns:
        [type]: `FileNotFoundError`: FileNotFoundError is returned when object path doesn't exist. If it does returns `None`.
    """

    for i in args:
        inp = ''.join(i)
        x = Path(inp)
        if not x.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), inp)

def sminp(inp, outext):
    """Check if input file has the same extension as the requested extension.

    Args:
        * `inp` ([type]: str): Input file
        * `outext` ([type]:str): Requested file type.

    Returns:
        [type]: `TypeError` if its the same.
    """

    f, f_ext = os.path.splitext(inp)    # Get file extension as str.
    if f_ext == outext:
        return TypeError(f'{f} file is already a {outext} file')

def inpchecker(inp1, inp2, ftype):
    """Wrapper for _format_check and _pathcheck. Checks the user inputs.

    Args:
        * `inp1` ([type]: any): First input.
        * `inp2` ([type]: any): Second input.
        * `ftype` ([type]: any): Variable format type.
    """
    _format_check(inp1, inp2, fmtype = ftype)  # Check if objects are of ftype.
    _pathcheck(inp1, inp2) # Check for the existance of the input paths.
