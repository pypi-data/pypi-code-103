__version__ = '0.1.0'


def get_version():
    """Get the package version string"""
    return __version__


def get_version_as_tuple():
    """Get the package version as tuple"""
    return tuple(map(int, __version__.split('.')))
