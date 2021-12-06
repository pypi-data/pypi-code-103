#
#  Copyright (C) 2021 IHS Markit.
#  All Rights Reserved
#

# the below is ported directly from commons - we can't use commons in the SDK as its unpublished (authorisation)
# https://gitlab.ihsmarkit.com/data-lake/python-commons/-/blob/master/datalake/commons/exceptions/view_exceptions.py
#
# we could add some build process for the published SDK, but its already complicated enough
# Never the less, these classes are done for us, so we want to use them
from typing import Optional

try:
    from flask import g, request, Request
    request_opt: Optional[Request] = request
except ImportError:
    g = None
    request_opt = None

try:
    from ddtrace.helpers import get_correlation_ids
except ImportError:
    get_correlation_ids = lambda: (None, None)


class BaseHttpException(Exception):
    description: Optional[str] = None
    details: Optional[str] = None
    title = 'Unknown error'
    status_code = 500

    def __init__(self, description=None, details=None, title=None):
        Exception.__init__(self)
        if title:
            self.title = title

        if description:
            self.description = description

        if isinstance(details, dict):
            self.details = [{k: self._flatten_message(v)} for k, v in details.items()]
        elif isinstance(details, list):
            self.details = str.join(', ', details)
        elif isinstance(details, str):
            self.details = details

    def to_dict(self):
        trace_id, span_id = get_correlation_ids()

        return_value = {
            'status': self.status_code,
            'title': self.title,
            'description': self.description,
            'details': self.details,
            'trace_id': trace_id,
            'span_id': span_id,
        }

        if request_opt:
            return_value['request_id'] = getattr(g, 'request_id', None)

        return dict((k, v) for k, v in return_value.items() if v is not None)

    def _flatten_message(self, message):
        if isinstance(message, list):
            return str.join(', ', message)
        elif isinstance(message, dict):
            for key, value in list(message.items()):
                message[key] = self._flatten_message(value)

        return message


INTERNAL_SERVER_ERROR_MESSAGE = (
    'Something went wrong. Please contact the Data Lake technical team by '
    'raising a request with datalake-support@ihsmarkit.com.'
)


class BadRequest(BaseHttpException):
    status_code = 400
    description = 'Request was incorrect.'
    title = 'Bad request'


class Unauthorized(BadRequest):
    status_code = 401
    description = 'Access to the resource requires authentication.'
    title = 'Unauthorized'


class Forbidden(BadRequest):
    status_code = 403
    description = 'There are restrictions on this operation. Please contact our Support team (Datalake-Support-Dataonboarding@ihsmarkit.com) to discuss your permissions.'
    title = 'Forbidden'


class NotFound(BadRequest):
    status_code = 404
    description = 'Entity was not found.'
    title = 'Not found'


class Conflict(BadRequest):
    status_code = 409
    description = 'There is a conflict.'
    title = 'Conflict'


class UnprocessableEntity(BadRequest):
    status_code = 422
    description = 'Request body is not valid, see details.'
    title = 'Unprocessable entity'


class InternalServerError(BaseHttpException):
    status_code = 500
    description = INTERNAL_SERVER_ERROR_MESSAGE
    title = 'Internal server error'


class NotImplemented(BaseHttpException):
    status_code = 501
    description = 'Functionality required to fulfil request is not supported.'
    title = 'Not implemented'
