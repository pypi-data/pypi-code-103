from dataclasses import dataclass

from cloudrail.cli.service.service_response_status import ResponseStatus


@dataclass
class ServiceResponse:
    status: ResponseStatus
    message: str

    @property
    def success(self):
        return self.status == ResponseStatus.SUCCESS


class ServiceResponseFactory:

    @staticmethod
    def success(message: str = None) -> ServiceResponse:
        return ServiceResponse(ResponseStatus.SUCCESS, message)

    @staticmethod
    def failed(message: str, status=ResponseStatus.FAILURE) -> ServiceResponse:
        return ServiceResponse(status, message)

    @staticmethod
    def unauthorized(message: str = None):
        return ServiceResponse(ResponseStatus.UNAUTHORIZED, message or 'Unauthorized. Please try to login again')
