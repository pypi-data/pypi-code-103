

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

    def _request(self, method, endpoint, filepath=None, **data):
        url = self.url(endpoint=endpoint)

        if filepath is not None:
            path = Path(filepath)
            with open(path, "rb") as file:
                files = {path.name(): file}
                result = method(url=url, files=files, data=data)
        else:
            result = method(url=url, data=data)

        self.store_session()
        # print(result.text)
        return result

    def post(self, endpoint, filepath=None, **data):
        """ :param endpoint: 
            :param filepath: Path to file or None. """
        return self._request(method=self.session.post, endpoint=endpoint, filepath=filepath, **data)

    def get(self, endpoint, filepath=None, **data):
        """ :param endpoint: 
            :param filepath: Path to file or None. """
        return self._request(method=self.session.get, endpoint=endpoint, filepath=filepath, **data)

    @staticmethod
    def render_response(response):
        """ Open response in browser. """
        path = Path.get_cache_dir() / "python/response.htm"  # type: Path
        path.text.write(response.text, overwrite=True)
        webbrowser.open(str(path))

    @staticmethod
    def response_to_file(response, path):
        """ Write a file from response to path. """
        name = re.findall("filename=(.+)", response.headers['content-disposition'])[0]
        path = Path(path) / name

        with open(path, "wb") as file:
            file.write(response.content)


