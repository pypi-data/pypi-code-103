try:
    import requests
except ImportError:
    raise ImportError('You don\'t have requests installed, '
                      'you can \"pip install requests\"'
                      'or see here https://docs.python-requests.org/en/latest/')
from enum import Enum


class ApiAbc:
    __slots__ = ('host', 'requests')
    _instance = None

    def __new__(cls, *args, **kwargs):
        """singleton mode"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host=None):
        self.host = host
        self.requests = requests.session()

    class Methods(str, Enum):
        """Methods Enum"""
        GET = "GET"
        POST = 'POST'
        PUT = 'PUT'
        PATCH = 'PATCH'
        DELETE = 'DELETE'

    def _full_uri(self, path):
        return f"{self.host}{path}"

    def _requests_abc(self, method, path, *args, **kwargs):
        """requests abstract"""
        return self.requests.request(method, self._full_uri(path), *args, **kwargs)

    def add_herders(self, key, value):
        self.requests.headers.update({key: value})
        print(f"headers are update {{ {key}:{value} }}")

    def get(self, path, *args, **kwargs):
        return self._requests_abc(self.Methods.GET, path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self._requests_abc(self.Methods.POST, path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return self._requests_abc(self.Methods.PUT, path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self._requests_abc(self.Methods.PATCH, path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return self._requests_abc(self.Methods.DELETE, path, *args, **kwargs)
