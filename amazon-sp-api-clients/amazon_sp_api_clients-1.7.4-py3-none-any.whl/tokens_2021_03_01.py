from .base import BaseClient as __BaseClient, convert_bool
from typing import List as _List


class CreateRestrictedDataTokenRequest:
    """
    The request schema for the createRestrictedDataToken operation.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        if "targetApplication" in data:
            self.targetApplication: str = str(data["targetApplication"])
        else:
            self.targetApplication: str = None
        if "restrictedResources" in data:
            self.restrictedResources: _List[RestrictedResource] = [
                RestrictedResource(datum) for datum in data["restrictedResources"]
            ]
        else:
            self.restrictedResources: _List[RestrictedResource] = []


class RestrictedResource:
    """
    Model of a restricted resource.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        if "method" in data:
            self.method: str = str(data["method"])
        else:
            self.method: str = None
        if "path" in data:
            self.path: str = str(data["path"])
        else:
            self.path: str = None
        if "dataElements" in data:
            self.dataElements: _List[str] = [str(datum) for datum in data["dataElements"]]
        else:
            self.dataElements: _List[str] = []


class CreateRestrictedDataTokenResponse:
    """
    The response schema for the createRestrictedDataToken operation.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        if "restrictedDataToken" in data:
            self.restrictedDataToken: str = str(data["restrictedDataToken"])
        else:
            self.restrictedDataToken: str = None
        if "expiresIn" in data:
            self.expiresIn: int = int(data["expiresIn"])
        else:
            self.expiresIn: int = None


class Error:
    """
    An error response returned when the request is unsuccessful.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        if "code" in data:
            self.code: str = str(data["code"])
        else:
            self.code: str = None
        if "message" in data:
            self.message: str = str(data["message"])
        else:
            self.message: str = None
        if "details" in data:
            self.details: str = str(data["details"])
        else:
            self.details: str = None


class ErrorList:
    """
    A list of error responses returned when a request is unsuccessful.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        if "errors" in data:
            self.errors: _List[Error] = [Error(datum) for datum in data["errors"]]
        else:
            self.errors: _List[Error] = []


class Tokens20210301Client(__BaseClient):
    def createRestrictedDataToken(
        self,
        data: CreateRestrictedDataTokenRequest,
    ):
        """
                Returns a Restricted Data Token (RDT) for one or more restricted resources that you specify. A restricted resource is the HTTP method and path from a restricted operation that returns Personally Identifiable Information (PII), plus a dataElements value that indicates the type of PII requested. See the Tokens API Use Case Guide for a list of restricted operations. Use the RDT returned here as the access token in subsequent calls to the corresponding restricted operations.
        **Usage Plans:**
        | Plan type | Rate (requests per second) | Burst |
        | ---- | ---- | ---- |
        |Default| 1 | 10 |
        |Selling partner specific| Variable | Variable |
        The x-amzn-RateLimit-Limit response header returns the usage plan rate limits that were applied to the requested operation. Rate limits for some selling partners will vary from the default rate and burst shown in the table above. For more information, see "Usage Plans and Rate Limits" in the Selling Partner API documentation.
        """
        url = f"/tokens/2021-03-01/restrictedDataToken"
        params = {}
        response = self.request(
            path=url,
            method="POST",
            params=params,
            data=data.data,
        )
        response_type = {
            200: CreateRestrictedDataTokenResponse,
            400: ErrorList,
            401: ErrorList,
            403: ErrorList,
            404: ErrorList,
            415: ErrorList,
            429: ErrorList,
            500: ErrorList,
            503: ErrorList,
        }[response.status_code]
        return None if response_type is None else response_type(self._get_response_json(response))
