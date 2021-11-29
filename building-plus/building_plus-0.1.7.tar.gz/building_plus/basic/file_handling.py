"""File handling utilities.

Functions:
ensure_dirpath
ensure_suffix
"""

import pathlib


def ensure_dirpath(filepath):
    """Returns the given filepath after creating the necessary
    directories for it to exist, if needed.

    Positional arguments:
    filepath - (pathlib.Path) Path to file or directory.
    """
    assert isinstance(
        filepath, pathlib.Path
    ), f"{filepath} is not a pathlib.Path instance."
    # Cannot use Path.is_dir() to check because it will return False for
    # a nonexistent directory.
    if filepath.suffix:
        # Probably a file, not a directory.
        dirpath = filepath.parent
    else:
        dirpath = filepath
    dirpath.mkdir(parents=True, exist_ok=True)
    return filepath


def ensure_suffix(filepath, suffix):
    """Return the given file path, ensuring that it has the given
    suffix. The returned file path has the same data type as the given
    one.

    Positional arguments:
    filepath - (pathlib.Path or str) The file path.
    suffix - (str) The suffix.
    """
    # Make sure suffix has a dot at the beginning.
    if suffix[0] != '.':
        suffix = '.' + suffix
    # Make sure pathlib.Path is used.
    str_input = isinstance(filepath, str)
    filepath = pathlib.Path(filepath)
    # Check suffix.
    if filepath.suffix != suffix:
        filepath = filepath.with_name(filepath.name + suffix)
    return str(filepath) if str_input else filepath
