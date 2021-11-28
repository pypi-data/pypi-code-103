"""Declares exception types."""
import uuid

from .schema import CanonicalExceptionSchema


class CanonicalException(Exception):
    """The base class for all exceptions."""

    #: The schema class used to convert the canonical exception to a
    #: dictionary.
    schema_class = CanonicalExceptionSchema

    #: The HTTP default HTTP status code.
    http_status_code = None

    #: The default code for the exception.
    code = 'UNCAUGHT_EXCEPTION'

    #: The default message.
    message = None

    #: The default detail.
    detail = None

    #: The default hint
    hint = None

    #: The default log message. String formatting is applied.
    log_message = "Caught fatal {code} (id: {id})"

    def __init__(self, id=None, code=None, message=None, detail=None, hint=None,
        http_status_code=None, **params):
        """Initialize a new :class:`CanonicalException`."""
        self.id = id or uuid.uuid4()
        self.code = code or self.code
        self.message = message or self.message
        self.detail = detail or self.detail
        self.hint = hint or self.hint
        self.http_status_code = http_status_code or self.http_status_code
        self.schema = self.schema_class()
        self.params = params

    def as_dict(self):
        """Return a dictionary containing the exception properties."""
        return self.schema.dump(self)

    def log(self, func, message=None):
        """Use `logger` to log the exception as `level`."""
        return func((message or self.log_message).format(**self.as_dict()))
