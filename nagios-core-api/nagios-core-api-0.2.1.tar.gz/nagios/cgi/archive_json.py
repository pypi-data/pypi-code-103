from .base import BaseCgi

class ArchiveJsonCgi(BaseCgi):
    def __init__(self, rest_client) -> None:
        super().__init__(rest_client)
        self.path = "archivejson.cgi"
