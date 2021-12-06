class AIAPIClientSDKException(Exception):
    """Base Exception class for AI API Client SDK exceptions"""
    pass


class AIAPIAuthenticatorException(AIAPIClientSDKException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.authenticator.Authenticator`"""
    pass


class AIAPIRequestException(AIAPIClientSDKException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient` if an unexpected
    exception occurs while trying to send a request to the server
    """
    pass


class AIAPIServerException(Exception):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient`, if a non-2XX
    response is received from the server.

    :param description: description of the exception
    :type description: str
    :param status_code: Status code of the response from the server
    :type status_code: int
    :param error_message: Error message received from the server
    :type error_message: str
    :param error_code: Error code received from the server, defaults to None
    :type error_code: str, optional
    :param request_id: ID of the request, the response belongs to, defaults to None
    :type request_id: str, optional
    :param details: Error details received from the server, defaults to None
    :type details: dict, optional
    """
    def __init__(self, description: str, status_code: int, error_message: str, error_code: str = None,
                 request_id: str = None, details: dict = None):
        super().__init__(f'{description}: {error_message}')
        self.description = description
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.details = details


class AIAPIAuthorizationException(AIAPIServerException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient` if a 401 response
    is received from the server. This extends the :class:`ai_api_client_sdk.exception.AIAPIServerException`, refer there
    for object definition
    """
    def __init__(self, description: str, error_message: str, error_code: str = None, request_id: str = None,
                 details: dict = None):
        super().__init__(description=description, status_code=401, error_code=error_code, error_message=error_message,
                         request_id=request_id, details=details)


class AIAPIInvalidRequestException(AIAPIServerException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient` if a 400 response
    is received from the server. This extends the :class:`ai_api_client_sdk.exception.AIAPIServerException`, refer there
    for object definition
    """
    def __init__(self, description: str, error_code: str, error_message: str, request_id: str, details: dict = None):
        super().__init__(description=description, status_code=400, error_code=error_code, error_message=error_message,
                         request_id=request_id, details=details)


class AIAPINotFoundException(AIAPIServerException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient` if a 404 response
    is received from the server. This extends the :class:`ai_api_client_sdk.exception.AIAPIServerException`, refer there
    for object definition
    """
    def __init__(self, description: str, error_code: str, error_message: str, request_id: str, details: dict = None):
        super().__init__(description=description, status_code=404, error_code=error_code, error_message=error_message,
                         request_id=request_id, details=details)


class AIAPIPreconditionFailedException(AIAPIServerException):
    """Exception type that is raised by the :class:`ai_api_client_sdk.helpers.rest_client.RestClient` if a 412 response
    is received from the server. This extends the :class:`ai_api_client_sdk.exception.AIAPIServerException`, refer there
    for object definition
    """
    def __init__(self, description: str, error_code: str, error_message: str, request_id: str, details: dict = None):
        super().__init__(description=description, status_code=412, error_code=error_code, error_message=error_message,
                         request_id=request_id, details=details)
