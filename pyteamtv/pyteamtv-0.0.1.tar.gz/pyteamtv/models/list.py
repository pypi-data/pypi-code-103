from typing import TypeVar, Type, Generic, Optional

from pyteamtv.infra.requester import Requester

T = TypeVar('T')


class List(Generic[T]):
    def __init__(self, content_class: Type[T], requester: Requester, method: str, url: str):
        data = requester.request(method, url)
        self._items = [content_class(
            requester,
            item
        ) for item in data]

    def __getitem__(self, index) -> T:
        assert isinstance(index, (int, slice))
        return self._items[index]

    def __iter__(self):
        for item in self._items:
            yield item

