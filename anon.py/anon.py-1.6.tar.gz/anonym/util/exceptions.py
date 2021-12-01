class NotLoggedIn(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class NotRegistered(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class Unauthorized(Exception):
    def __init__(self):
        super().__init__("Unauthorized")


class ChatNotCreated(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Unknown(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class MessageSendingError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class LikeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class InvalidCommentLenght(Exception):
    def __init__(self):
        super().__init__("Comment must be at least three characters long")

class CommentingError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class ViewError(Exception):
    def __init__(self, message: str):
        super().__init__(message)