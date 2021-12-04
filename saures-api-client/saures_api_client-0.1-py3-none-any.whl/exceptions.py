class Error(BaseException):
    message: str


class ClientError(Error):
    def __init__(self, message):
        self.message = message


class RetryLimitExceeded(ClientError):
    message = "Maximum retry limit exceeded."


class WrongCredsException(ClientError):
    pass


class NoPagesLeft(Error):
    def __init__(self):
        super().__init__("No pages left to scroll.")


class AbstractException(ClientError):
    pass
