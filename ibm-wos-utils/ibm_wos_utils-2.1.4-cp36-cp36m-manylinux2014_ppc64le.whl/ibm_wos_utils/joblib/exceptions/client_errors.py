# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

class ClientError(Exception): 
    """Base class for exceptions in joblib."""
    
    def __init__(self, message, error=None):
        self.message = message
        self.error = error
    
    def __str__(self):
        return str(self.message) + ("\nError: " + str(self.error) if self.error is not None else "")

class BadRequestError(ClientError):
    """Exception raised for invalid input to joblib."""
    def __init__(self, message, error=None):
        super().__init__(message, error=error)

class ObjectNotFoundError(ClientError):
    """Exception raised when reuested object could not be found."""
    def __init__(self, message, error=None):
        super().__init__(message, error=error)

class DependentServiceError(ClientError):
    """Exception raised when call to dependent services fail."""
    def __init__(self, message, response, error=None):
        self.response = response
        message = "{} ({} {})\nStatus code: {}, body: {}".format(message, response.request.method, response.request.url, response.status_code, response.text if response.apparent_encoding is not None else "[binary content, " + str(len(response.content)) + " bytes]")
        super().__init__(message, error=error)

class MissingValueError(ClientError, ValueError):
    def __init__(self, field, error=None):
        ClientError.__init__(self, "Value for {} is not provided.".format(field), error)

class InvalidInputError(ClientError, ValueError):
    def __init__(self, field, error=None):
        ClientError.__init__(self, "The value provided for {} is invalid.".format(field), error)

class UnexpectedTypeError(ClientError, ValueError):
    def __init__(self, field, expected_type, actual_type):
        ClientError.__init__(self, "Unexpected type of '{}' is specified, expected: {}, actual: '{}'.".format(field, expected_type, actual_type))

class UnsupportedOperationError(ClientError):
    """Exception raised for unsupported operation is requested."""
    def __init__(self, operation_name, error=None):
        super().__init__("The requested operation({}) is not supported.".format(operation_name), error=error)

class NotImplementedError(ClientError):
    """Exception raised for operation requested is not yet implemented."""
    def __init__(self, operation_name, error=None):
        super().__init__("The requested operation({}) is not yet implemented.".format(operation_name), error=error)

class MaxRetryError(ClientError):
    """Exception raised if requested operation did not succeed even after retries."""
    def __init__(self, operation_name, error=None):
        super().__init__("Max retries exceeded for the requested operation {}.".format(operation_name), error=error)
