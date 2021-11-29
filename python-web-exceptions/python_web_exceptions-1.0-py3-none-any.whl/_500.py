from typing import Optional

from .base_http_exception import BaseHttpException


class InternalServerException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(500, message, header)


class NotImplimentedException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(501, message, header)


class BadGatewayException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(502, message, header)


class GatewayTimeoutException(BaseHttpException):

    def __init__(self, message: str, header: Optional[str] = None):
        super().__init__(504, message, header)
