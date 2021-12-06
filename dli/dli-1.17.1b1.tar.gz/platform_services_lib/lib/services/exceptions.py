#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
try:
    import simplejson as json  # noqa: I900
except ImportError:
    import json  # type: ignore
except:
    pass


class ServiceException(Exception):
    def __init__(self, details: str):
        super(ServiceException, self).__init__(details)
        self.details = details


class SchemaMismatchException(Exception):
    def __init__(self, details):
        super(SchemaMismatchException, self).__init__(details)
        self.details = details


class NoResourceFound(ServiceException):
    pass


class UnsupportedDatasetLocation(ServiceException):
    pass


class UnableToAccessDataset(ServiceException):
    pass


class UnableToAuthenticateToS3(ServiceException):
    pass


class UnableToParsePartition(ServiceException):
    pass


class CacheException(ServiceException):
    pass


class InterfaceResourceUnavailable(ServiceException):
    def __init__(self, details: str, status: int):
        super().__init__(details)
        self.status = status


# cache specific


class NoKeyInCache(CacheException):
    pass


class CacheInconsistent(CacheException):
    pass


# sdk specific (right now)


class DatalakeException(Exception):
    def __init__(self, entity=None, params=None, message=None, response=None):
        if not params and not message:
            message = "%s not found" % entity

        self.params = params
        self.message = (
            message or 'entity with params `{}` not found'.format(params)
        )
        self.entity = entity
        self.response = response

        super(DatalakeException, self).__init__(
            self.message, entity,
            params, message
        )

    def __str__(self):
        error = '\nProblem with the call to: ' \
                f'{self.response.request.method} {self.response.request.url}' \
                '\nPlease do not copy this URL into a browser. ' \
                "If you need more help please contact support at " \
                "datalake-support@ihsmarkit.com with this error message " \
                "including any request_id. \n\n"

        try:
            error += (
                f'{json.dumps(self.response.json(), indent=4)}'
            )

        except json.JSONDecodeError:
            error += (
                f'{self.response.text}'
            )

        try:
            request_id = self.response.request.headers.get(
                'X-Request-ID', 'unknown'
            )

            error += (
                f'\nProvided request_id: {request_id}\n'
            )
        except Exception:
            error += (
                f'\nProvided request_id: Unknown\n'
            )

        return error


class DatalakePayloadTooLargeException(DatalakeException):

    def __str__(self):
        error = super().__str__()
        if self.response.status_code == 413:
            error += (
                '\nA file you are attempting to pass is probably too large for our server.'
                ' If passing a sample_data file please make sure it is under 10 Megabytes.\n\n'
            )

        return error


class DataframeStreamingException(DatalakeException):

    def __init__(self, error, url, entity=None, params=None, message=None,
                 response=None):
        self.url = url
        self.error = error
        super().__init__(
            entity=entity,
            params=params,
            message=message,
            response=response
        )

    def __str__(self):
        msg = json.dumps(self.error, indent=4)
        return f'\n A GET request was made to the following url: ' \
               f'{self.url}' \
               '\nPlease do not copy this URL into a browser. ' \
               "If you need more help please contact support at " \
               "datalake-support@ihsmarkit.com with this error message " \
               "including any request_id. \n\n" \
               f'\n\n{msg}'


class ConnectionException(DatalakeException):
    pass


class CatalogueEntityNotFoundException(DatalakeException):
    pass


class InvalidPayloadException(DatalakeException):
    pass


class UnAuthorisedAccessException(DatalakeException):
    pass


class DatalakeGatewayTimeout(DatalakeException):
    def __str__(self):
        error = super().__str__()
        error += (
            '\nThis request to the Datalake has timed-out. This means that the '
            'request required too much processing or our service is under heavy '
            'load. Your request may still be running on the server, if so we '
            'will attempt to cache the results and you should try the same call '
            'again in five minutes. If the problem persists then please report '
            'this error to a member of the Datalake support team.'
        )
        return error


class DatalakeServiceUnavailable(DatalakeException):

    def __str__(self):
        error = super().__str__()
        error += '\nIHS Markit datalake is unavailable. Please try again in a few seconds.'
        return error


class InsufficientPrivilegesException(DatalakeException):

    def __str__(self):
        error = super().__str__()
        error += '\nInsufficient privileges to perform this action'
        return error


class S3FileDoesNotExist(DatalakeException):
    def __init__(self, file_path):
        self.message = (
            "Either file at path `%s` does not exist / Potential issue with the bucket policy."
            "Please reach out to Datalake Tech Data Ops user for resolution." % file_path
        )

        super(S3FileDoesNotExist, self).__init__(self.message)


class S3BucketDoesNotExist(DatalakeException):
    def __init__(self, bucket_name):
        self.message = (
            "Either bucket at path `%s` does not exist / Potential issue with the bucket policy."
            "Please reach out to Datalake Tech Data Ops user for resolution." % bucket_name
        )

        super(S3BucketDoesNotExist, self).__init__(self.message)


class DownloadFailed(DatalakeException):
    pass
