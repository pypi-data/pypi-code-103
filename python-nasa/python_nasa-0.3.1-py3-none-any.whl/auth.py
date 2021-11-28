from hashlib import sha256
from typing import Any, Text
from requests.auth import AuthBase
from requests.models import PreparedRequest


class NASAAuth(AuthBase):
    def __init__(self, api_key: Text = "DEMO_KEY") -> None:
        self.__api_key: Text = api_key

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.prepare_url(request.url, {"api_key": self.__api_key})
        return request

    def __eq__(self, obj: Any) -> bool:
        return hash(self) == hash(obj)

    def __hash__(self) -> int:
        return hash(self.__api_key)

    def __str__(self) -> str:
        checksum: Text = sha256(self.__api_key.encode()).hexdigest()
        string: Text = f"NASAAuth(API Key Checksum = {checksum}"
        return string

    def __repr__(self) -> str:
        return str(self)
