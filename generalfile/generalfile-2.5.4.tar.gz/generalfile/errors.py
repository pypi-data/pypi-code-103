
class _MiddleGroundError(Exception):
    """Parent of all middle ground errors."""


class CaseSensitivityError(_MiddleGroundError):
    """Raised when an existing file matches a path but not the exact case."""


class InvalidCharacterError(_MiddleGroundError):
    """Raised when using an invalid character."""





