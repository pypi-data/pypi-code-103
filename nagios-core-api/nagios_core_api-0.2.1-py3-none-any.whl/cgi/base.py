import logging
from nagios.exceptions import NagiosUnexpectedResultError

logging.getLogger("nagios").addHandler(logging.NullHandler())

class BaseCgi:
    def __init__(self, rest_client) -> None:
        self.path = None
        self.rest_client = rest_client

    def _result_handler(self, response):
        result = response.get("result", {})
        code = result.get("type_code")
        text = result.get("type_text").lower()

        if code != 0 and text != "success":
            logging.debug("Unexpected Result: %s -> %s", code, text)
            raise NagiosUnexpectedResultError("Nagios unexpected error occurred")
        
        return response
