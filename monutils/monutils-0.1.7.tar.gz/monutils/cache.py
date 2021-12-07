from abc import ABC, ABCMeta
from typing import Any, List, Dict
from pymongo.collection import Collection

from mysutils.method import synchronized


class MongoCache(ABC):
    """ Abstract class to create a cache from a MongoDB collection. """
    __metaclass__ = ABCMeta

    @property
    def size(self) -> int:
        """
        :return: The cache size.
        """
        return self.__size

    @property
    def collection(self) -> Collection:
        """
        :return: The collection to create the cache.
        """
        return self.__collection

    def __init__(self, collection: Collection, size: int = 0) -> None:
        """  Constructor.

        :param collection: The collection to create the cache.
        :param size: The cache size. If 0, then, all the registers are cached.
        """
        self.__collection: Collection = collection
        self.__size: int = size
        self._cache: Dict[Any, Any] = {}
        self.__ordered: List[Any] = []

    @synchronized
    def add(self, key: Any, value: Any) -> None:
        """  Add our update a register to the cache.

        :param key: The key to search.
        :param value: The register to cache.
        """
        if not self.update(key, value):
            if self.size and self.size >= len(self.__ordered):
                del self._cache[self.__ordered[0]]
                del self.__ordered[0]
            self.__ordered.append(key)
            self._cache[key] = value

    @synchronized
    def update(self, key: Any, value: Any) -> bool:
        """ Update a cached register.

        :param key: The key to search.
        :param value: The value to update.
        :return: True if it was updated. False if the registers wasn't previously cached and there is nothing to cache.
        """
        if key in self._cache:
            self._cache[key] = value
            return True
        return False

    def __setitem__(self, key: Any, value: Any) -> None:
        """  Add a register to the cache.

        :param key: The key to search.
        :param value: The register to cache.
        """
        self.add(key, value)

    def __getitem__(self, key: Any) -> Any:
        """ Return a cached register.

        :param key: The key to search.
        :return: The cached register.
        :raises KeyError: If a register with that key was not previously cached.
        """
        return self._cache[key]

    def __contains__(self, key: Any) -> bool:
        """ If a register was cached.

        :param key: The key to search.
        :return: True if the key is in the cache, otherwise False.
        """
        return key in self._cache

    def __len__(self) -> int:
        """
        :return: The len of the cache.
        """
        return len(self.__ordered)
