"""For reading example files."""

import shutil

from eagers.config.path_spec import DEMO_FILES_DIR, USER_DIR_LOCATION


def load_example_file(filename, cache_name, overwrite_cache=False):
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
    overwrite_cache - (bool) (Default: False) If True, overwrite the
        data set with the file in the demo_files directory.
    """
    cache_location = USER_DIR_LOCATION.get(cache_name)
    if not cache_location:
        raise ValueError(f"Invalid cache name {cache_name!r}")
    cache_path = cache_location / filename

    if overwrite_cache or not cache_path.exists():
        demo_file_path = DEMO_FILES_DIR / filename
        assert demo_file_path.exists(), f"{demo_file_path!r} does not exist"
        shutil.copyfile(demo_file_path, cache_path)

    return cache_path
