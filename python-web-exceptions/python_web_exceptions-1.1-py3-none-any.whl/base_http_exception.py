from typing import Optional, Union


class BaseHttpException(Exception):

    status_code: int
    message: str
    header: Union[str, None]

    def __init__(self, status_code: int, message: str, header: Optional[str] = None) -> None:
        self.status_code = status_code
        self.message = message
        self.header = header
    
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if (self.header is None):
            return f"{class_name}(status_code={self.status_code}, message={self.message})"
        else:
            return f"{class_name}(status_code={self.status_code}, message={self.message}, header={self.header})"

    def dict(self):
        if (self.header is not None):
            return {"status-code": self.status_code, "message": self.message, "header": self.header}
        else:
            return {"status-code": self.status_code, "message": self.message}
