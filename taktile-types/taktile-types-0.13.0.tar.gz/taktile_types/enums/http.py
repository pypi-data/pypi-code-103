"""Enums about HTTP"""

from taktile_types.enums.common import ExtendedEnum


class Method(ExtendedEnum):
    """HTTP Methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
