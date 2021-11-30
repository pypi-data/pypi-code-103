from functools import lru_cache
from robot.version import VERSION as ROBOT_VERSION
from docgen import utils


if int(ROBOT_VERSION[0]) >= 4:
    from robot.libdocpkg.robotbuilder import LibraryDocBuilder

    def _build(value):
        return LibraryDocBuilder().build(value)


else:
    from robot.libdocpkg import LibraryDocumentation

    def _build(value):
        return LibraryDocumentation(value)


@lru_cache(maxsize=None)
def load(value):
    """Parse library into container, with caching."""
    try:
        with utils.silent():
            return _build(str(value))
    except (Exception, SystemExit):
        utils.debug_traceback()
        raise ImportError(f"Failed to load library: {value}")
