class DynamodbStreamRouterException(Exception):
    pass


class KeywordError(DynamodbStreamRouterException):
    pass


class RouteAlreadyExistsException(DynamodbStreamRouterException):
    pass


class SyntaxError(DynamodbStreamRouterException):
    pass
