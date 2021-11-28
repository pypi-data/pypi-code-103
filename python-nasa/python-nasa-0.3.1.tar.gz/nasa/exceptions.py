from typing import Text, Type


class BaseNASAException(Exception):
    CODE: Text = "NASA-ERROR-001"

    def __init__(self, message: Text) -> None:
        coded_message: Text = f"{self.CODE} - {message}"
        super().__init__(coded_message)


class NASAHTTPError(BaseNASAException):
    CODE: Text = "NASA-ERROR-002"


class NASAInvalidInput(BaseNASAException):
    CODE: Text = "NASA-ERROR-003"


class NASAContentTypeNotImage(BaseNASAException):
    CODE: Text = "NASA-ERROR-004"


class NASAUnidentifiedError(BaseNASAException):
    CODE: Text = "NASA-ERROR-999"

    def __init__(self, message: Text, error_type: Type) -> None:
        typed_message: Text = f"{error_type.__name__} - {message}"
        super().__init__(typed_message)
