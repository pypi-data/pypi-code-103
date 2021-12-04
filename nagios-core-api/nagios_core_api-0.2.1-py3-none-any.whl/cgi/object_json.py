from .base import BaseCgi

class ObjectJsonCgi(BaseCgi):
    def __init__(self, rest_client) -> None:
        super().__init__(rest_client)
        self.path = "object.cgi"
