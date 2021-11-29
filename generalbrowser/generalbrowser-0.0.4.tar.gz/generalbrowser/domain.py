

from requests import Session
import webbrowser
import re

from generalfile import Path
from generallibrary import AutoInitBases


class Domain(metaclass=AutoInitBases):
    """ Client methods to talk to API. """
    session_path = Path.get_cache_dir() / "python/session.txt"
    def __init__(self, domain):
        self.domain = domain

        stored_session = self.session_path.pickle.read(default=None)
        self.session = stored_session or Session()

    def url(self, endpoint):
        return f"{self.domain}/api/{endpoint}"

    def store_session(self):
        self.session_path.pickle.write(self.session, overwrite=True)

    def _request(self, method, endpoint, files=None, **data):
        url = self.url(endpoint=endpoint)
        result = method(url=url, files=files, data=data)
        self.store_session()
        # print(result.text)
        return result

    def post(self, endpoint, files=None, **data):
        """ :param endpoint: 
            :param files: Dict of files or None. """
        return self._request(method=self.session.post, endpoint=endpoint, files=files, **data)

    def get(self, endpoint, files=None, **data):
        """ :param endpoint: 
            :param files: Dict of files or None. """
        return self._request(method=self.session.get, endpoint=endpoint, files=files, **data)

    @staticmethod
    def render_response(response):
        """ Open response in browser. """
        path = Path.get_cache_dir() / "python/response.htm"  # type: Path
        path.text.write(response.text, overwrite=True)
        webbrowser.open(str(path))

    @staticmethod
    def file_to_request(name, path):
        """ Return a dictionary of files to be used in request. """
        path = Path(path)
        with open(path, "rb") as file:
            return {name: file}

    @staticmethod
    def response_to_file(response, path):
        """ Write a file from response to path. """
        name = re.findall("filename=(.+)", response.headers['content-disposition'])[0]
        path = Path(path) / name

        with open(path, "wb") as file:
            file.write(response.content)


