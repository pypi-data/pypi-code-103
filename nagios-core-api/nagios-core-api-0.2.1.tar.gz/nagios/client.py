from nagios.rest_client import RestClient
from nagios.cgi import ArchiveJsonCgi, ObjectJsonCgi, StatusJsonCgi


class Nagios:
    def __init__(self, url, username, password) -> None:
        self.url = url
        self.rest_client = RestClient(self.url, username, password)
        self.archive = ArchiveJsonCgi(rest_client=self.rest_client)
        self.object = ObjectJsonCgi(rest_client=self.rest_client)
        self.status = StatusJsonCgi(rest_client=self.rest_client)
    
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, value):
        self._url = f"{value}/cgi-bin"

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.rest_client._close_session()
