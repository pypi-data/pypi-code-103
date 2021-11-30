from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

from cloudrail.cli.service.service_response_status import ResponseStatus


@dataclass
class BaseCloudrailResponse:
    status: ResponseStatus

    @property
    def success(self):
        return self.status == ResponseStatus.SUCCESS


@dataclass
class CloudrailErrorResponse(BaseCloudrailResponse):
    message: str = ''
    status: ResponseStatus = ResponseStatus.FAILURE


@dataclass
class CloudrailSuccessJsonResponse(BaseCloudrailResponse):
    data: DataClassJsonMixin = None
    status: ResponseStatus = ResponseStatus.SUCCESS


@dataclass
class CloudrailSuccessDataResponse(BaseCloudrailResponse):
    data: str = None
    status: ResponseStatus = ResponseStatus.SUCCESS


@dataclass
class CloudrailUnauthorizedResponse(BaseCloudrailResponse):
    message: str = 'Unauthorized. Please try to login again'
    status: ResponseStatus = ResponseStatus.UNAUTHORIZED
