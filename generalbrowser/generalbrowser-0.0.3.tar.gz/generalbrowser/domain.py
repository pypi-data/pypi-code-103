

from requests import Session

from generalfile import Path


class Domain:
    session_path = Path.get_cache_dir() / "python/session.txt"
    def __init__(self, domain):
        self.domain = domain

        stored_session = self.session_path.pickle.read(default=None)
        self.session = stored_session or Session()

    def url(self, endpoint):
        return f"{self.domain}/api/{endpoint}"

    def store_session(self):
        self.session_path.pickle.write(self.session, overwrite=True)

    def _request(self, method, endpoint, **data):
        url = self.url(endpoint=endpoint)
        result = method(url=url, data=data)
        self.store_session()
        # print(result.text)
        return result

    def post(self, endpoint, **data):
        return self._request(method=self.session.post, endpoint=endpoint, **data)

    def get(self, endpoint, **data):
        return self._request(method=self.session.get, endpoint=endpoint, **data)

