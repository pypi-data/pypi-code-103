from typing import Optional

from .base_http_exception import BaseHttpException


class BadRequestException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(400, message, header)


class UnauthorisedException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(401, message, header)


class ForbiddenException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(403, message, header)


class NotFoundException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(404, message, header)


class TimeoutException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(408, message, header)


class ConflictException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(409, message, header)


class PayloadTooLargeException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(413, message, header)   