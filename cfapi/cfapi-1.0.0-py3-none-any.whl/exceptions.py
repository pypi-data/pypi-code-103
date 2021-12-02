class CFApiException(Exception):
    """Base exception for all custom exceptions raise by the cfapi module."""


class InvalidIdentifierException(CFApiException, ValueError):
    """Raised when trying to load data from an invalid URL (probably because the
    data doesn't exist or isn't public)."""


class InvalidURL(CFApiException, ValueError):
    """Raised when typing to load a data using a given URL, but the URL isn't a
    valid one."""
