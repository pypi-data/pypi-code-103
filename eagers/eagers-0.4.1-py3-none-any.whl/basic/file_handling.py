"""File handling utilities.

Functions:
ensure_dirpath
ensure_suffix
find_file_in_tree
find_file_in_userdir
"""

import os
import pathlib

from eagers.config.user import USER_DIR_EXCLUDE_NAME


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


def ensure_suffix(filepath, suffix, remove_bad_suffix=False):
    """Return the given file path, ensuring that it has the given
    suffix. The returned file path has the same data type as the given
    one.

    Positional arguments:
    filepath - (pathlib.Path or str) The file path.
    suffix - (str) The suffix.

    Keyword arguments:
    remove_bad_suffix - (bool) (Default: False) Whether to replace the
        current with the correct one, or to simply append the correct
        one. WARNING: Setting this to True can result in unexpected
        behavior if the filename contains dots.
    """
    # Make sure suffix has a dot at the beginning.
    if suffix[0] != '.':
        suffix = '.' + suffix
    # Make sure pathlib.Path is used.
    str_input = isinstance(filepath, str)
    filepath = pathlib.Path(filepath)
    # Check suffix.
    if filepath.suffix != suffix:
        if remove_bad_suffix:
            filepath = filepath.with_name(filepath.stem + suffix)
        else:
            filepath = filepath.with_name(filepath.name + suffix)
    return str(filepath) if str_input else filepath


def find_file_in_tree(dir_, filename, exclude_dirs=None):
    """Find the given file name in the file tree rooted at the given
    directory. Returns the path to the file. If the file does not exist,
    a ValueError is raised. If more than one instance of the file
    exists, a RuntimeError is raised.

    Positional arguments:
    dir_ - (pathlib.Path) Path to tree root directory.
    filename - (str) Name of file.

    Keyword arguments:
    exclude_dirs - (list of str) Directories to exclude from search.
    """
    # Handle input.
    if not exclude_dirs:
        exclude_dirs = []
    # Search directory tree.
    found = False
    found_dir = None
    for root, dirs, files in os.walk(ensure_dirpath(dir_)):
        if root.rsplit(os.sep, maxsplit=1)[-1] in exclude_dirs:
            # dirs list must be modified in-place; not reassigned.
            for i in range(len(dirs)):
                del dirs[0]
        elif filename in files:
            if found:
                dirname = lambda d: d.rsplit(os.path.sep, maxsplit=1)[1]
                raise RuntimeError(
                    f"{filename!r} found in at least two directories: "
                    f"{dirname(found_dir)!r}, {dirname(root)!r}")
            found = True
            found_dir = root
    if not found:
        raise ValueError(f"{filename!r} not in {dir_.name!r}")
    return pathlib.Path(found_dir) / filename


def find_file_in_userdir(subdir, filename, suffix):
    """Find the file with the given name in the given sub-directory of
    the user directory.

    Positional arguments:
    subdir - (pathlib.Path) Sub-directory of user directory.
    filename - (str) File name.
    suffix - (str) File suffix.
    """
    return find_file_in_tree(
        subdir,
        ensure_suffix(filename, suffix),
        exclude_dirs=USER_DIR_EXCLUDE_NAME,
    )
