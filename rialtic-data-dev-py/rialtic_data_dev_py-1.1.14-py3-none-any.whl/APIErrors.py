from enum import Enum
from http import HTTPStatus
import requests

class DevAPIErrorCode(Enum):
    InvalidClientTokenId = "InvalidClientTokenId"    # API key for SDK is not valid
    Throttling = "Throttling"                        # The request was denied due to request throttling
    InternalError = "InternalError"                  # Internal processing error
    ServiceUnavailable = "ServiceUnavailable"        # Query service is not available
    MalformedQueryString = "MalformedQueryString"    # Query string contains a syntax error
    InvalidQueryParameter = "InvalidQueryParameter"  # Query is not valid
    InvalidParameterValue = "InvalidParameterValue"  # One or more of the values in the request is not valid
    Unauthorized = "Unauthorized"                    # Denied due to insufficient permissions or absent subscription

class DevAPIError:
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

def ReadAPIErrorFromHTTPResponse(response: requests.Response) -> DevAPIError:
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return _readFromResponseContents(response)

    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        return DevAPIError(DevAPIErrorCode.InternalError, 'Received 401 from API gateway')

    elif response.status_code == HTTPStatus.FORBIDDEN:
        return DevAPIError(DevAPIErrorCode.InvalidClientTokenId, 'Received 403 from API gateway')

    elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        return DevAPIError(DevAPIErrorCode.Throttling, 'Received 429 from API gateway')

    else:
        message = 'Received %s from API gateway: %s' % (response.status_code, response.text)
        return DevAPIError(DevAPIErrorCode.InternalError, message)

def _readFromResponseContents(response: requests.Response) -> DevAPIError:
    respJSON = response.json()
    if "error_code" in respJSON and "message" in respJSON:
        return DevAPIError(DevAPIErrorCode[respJSON["error_code"]], respJSON["message"])
    else:
        return DevAPIError(DevAPIErrorCode.InternalError, response.text)
