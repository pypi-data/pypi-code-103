import random
import string
from vtb_py_logging.log_extra import get_extra

REQUEST_ID_HEADER = "X-Request-Id"
DEFAULT_SIZE = 10
DEFAULT_DELIMITER = "#"
MIN_RANDOM_SIZE = 4
ALLOWED_CHARS = string.ascii_uppercase + string.digits + string.ascii_lowercase


def _random(chars, length):
    return "".join([random.choice(chars) for _ in range(length)])


class RequestId:
    @classmethod
    def make(cls, *, size=None, prefix=None, suffix=None, delimiter=DEFAULT_DELIMITER, chars=None):
        prefix_delimiter = ""
        suffix_delimiter = ""
        size = size or DEFAULT_SIZE
        length = 0
        if prefix:
            prefix_delimiter = delimiter
            length += len(prefix) + 1
        if suffix:
            suffix_delimiter = delimiter
            length += len(suffix) + 1
        chars = chars or ALLOWED_CHARS
        generated_size = max(size - length, MIN_RANDOM_SIZE)
        request_id = "".join((prefix or "",
                              prefix_delimiter,
                              _random(chars, generated_size),
                              suffix_delimiter,
                              suffix or ""
                              ))
        return request_id

    @classmethod
    def make_subrequest(cls, request_id, *, suffix=None, delimiter=DEFAULT_DELIMITER, chars=None, size=None):
        if suffix:
            request_id += DEFAULT_DELIMITER + suffix
        sub_id = _random(chars or ALLOWED_CHARS, size or MIN_RANDOM_SIZE)
        return delimiter.join((request_id, sub_id))


def get_context_request_id():
    return get_extra().get("request_id")


def get_request_id_header():
    request_id = get_context_request_id()
    return {REQUEST_ID_HEADER: request_id} if request_id else {}
