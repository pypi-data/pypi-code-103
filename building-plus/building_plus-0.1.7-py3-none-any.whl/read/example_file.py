"""For reading example files."""

import shutil

from building_plus.basic.file_handling import ensure_suffix
from building_plus.config.path_spec import DEMO_FILES_DIR, USER_DIR_LOCATION


def load_example_file(filename, cache_name, suffixes=None, overwrite_cache=False):
    """Load an example dataset from either the cache or the demo_files
    folder included in the repository.

    This function provides quick access to an example data set that is
    useful for helping a new user get started.

    Returns a pathlib.Path object pointing to the requested file in the
    example files cache directory.

    Positional arguments:
    filename - (str) Name of the data set with its file suffix.
    cache_name - (str) Name of cache to write to.

    Keyword arguments:
    suffixes - (Collection of str) (Default: None) Acceptable suffixes.
        If used, the filename should not have a suffix already.
    overwrite_cache - (bool) (Default: False) If True, overwrite the
        data set with the file in the demo_files directory.
    """
    cache_location = USER_DIR_LOCATION.get(cache_name)
    if not cache_name:
        raise ValueError(f"Invalid cache name {cache_name!r}")
    any_suffixes_not_cached = False
    if not overwrite_cache:
        if suffixes:
            any_suffixes_not_cached = any(
                not (cache_location / ensure_suffix(filename, s)).exists()
                for s in suffixes
            )
        else:
            any_suffixes_not_cached = not (cache_location / filename).exists()

    if overwrite_cache or any_suffixes_not_cached:
        # Copy all files matching the given suffixes from the demo directory into the
        # cache.  If overwrite_cache is False, any files that are already cached will
        # not be overwritten.
        if suffixes:
            suffixed_filenames = (ensure_suffix(filename, s) for s in suffixes)
        else:
            suffixed_filenames = iter([filename])
        for suffixed in suffixed_filenames:
            cache_path = cache_location / suffixed
            if not cache_path.exists() or overwrite_cache:
                # Write from demo directory to cache.
                demo_file_path = DEMO_FILES_DIR / suffixed
                assert demo_file_path.exists(), f"{demo_file_path!r} does not exist"
                shutil.copyfile(demo_file_path, cache_path)

    # filename should not have been modified, so that if no suffix was put on the
    # filename, the cache path will also be returned without a suffix.
    return cache_location / filename
