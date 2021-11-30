class HossException(Exception):
    pass


class NotAuthorizedException(HossException):
    pass


class NotFoundException(HossException):
    pass


class AlreadyExistsException(HossException):
    pass

