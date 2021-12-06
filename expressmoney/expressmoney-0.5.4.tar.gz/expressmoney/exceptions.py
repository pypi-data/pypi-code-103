from rest_framework import status
from rest_framework.exceptions import APIException


class UnknownException(APIException):
    pass


class ServiceUnavailable(UnknownException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Remote Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class ServiceError(UnknownException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Remote Service API has changed'
    default_code = 'service_api_error'
