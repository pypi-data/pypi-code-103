from abc import ABC, abstractmethod
from functools import lru_cache as cache

import requests
from bs4 import BeautifulSoup


from .exceptions import InvalidIdentifierException, InvalidURL

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, TypeVar, Optional

    T = TypeVar("T")


class Base(ABC):

    BASE_URL = "https://codeforces.com/"

    def __init__(self, identifier: "T") -> None:
        self.__id = identifier

    @property
    def identifier(self) -> "T":
        """A unique identifier that is used to generaate the content URL."""
        return self.__id

    @classmethod
    @abstractmethod
    def identifier_from_url(cls, url: str) -> "Optional[T]":
        """Returns the identifier from the given url. If the identifier can't be
        found, returns None."""

    @classmethod
    def from_url(cls: "Type[T]", url: str) -> "T":
        """Recives a URL as a string, and returns an instance of the of API
        object that represents the information in the given URL."""

        result = cls.identifier_from_url(url)
        if result is None:
            raise InvalidURL(f"Invalid URL {url!r} for {cls.__name__!r}")
        else:
            return cls(result)

    @property
    @abstractmethod
    def url(self):
        """The URL to the page where the information is scraped from."""

    @property
    @cache
    def data(self) -> BeautifulSoup:
        """Sends a https request to scrape the data of the object. By default,
        the data is lazy-loaded, and this method is called only when required
        by other methods."""

        data = requests.get(self.url, allow_redirects=False)
        if data.status_code != 200:
            raise InvalidIdentifierException(
                f"Invalid identifier {self.identifier!r} for {type(self).__name__!r} "
                "(Resource doesn't exist or isn't public).",
            )

        return BeautifulSoup(data.content, "lxml")

    def __repr__(self):
        return f"<{type(self).__name__} {self.identifier}>"
