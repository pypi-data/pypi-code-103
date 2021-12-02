import copy
import json
import threading
from typing import Any, Dict

from .base import BaseContext


class ThreadLocalContext(BaseContext):
    serializer = json.dumps

    def __init__(self) -> None:
        self.__thread_local_data = threading.local()
        self.__thread_local_data.data = {}
        self.__thread_local_data.serialized_data = "{}"

    def get_value(self, key: str, clear: bool = False):
        """Return value of given key if exist

        Args:
            key (str): The key which you want to retrieve
            clear (bool, optional): If `clear=True`, remove the value after it is retrieved. Defaults to False.

        Raises:
            LookupError: If the value does not exist
        """
        if not hasattr(self.__thread_local_data, "data"):
            self.__thread_local_data.data = {}
        try:
            value = self.__thread_local_data.data[key]
            self.__thread_local_data.data.pop(key)
            return value
        except KeyError:
            raise LookupError(f"Key {key} is not in context")

    def _serialize_data(self):
        if not hasattr(self.__thread_local_data, "data"):
            return ""
        self.__thread_local_data.serialized_data = ThreadLocalContext.serializer(self.__thread_local_data.data)

    def set_value(self, key: str, value: Any) -> None:
        """Set a value into context

        Args:
            key (str): The key which you want to set
            value (Any): The value you want to set
        """
        if not hasattr(self.__thread_local_data, "data"):
            self.__thread_local_data.data = {}
        self.__thread_local_data.data[key] = value
        self._serialize_data()

    def delete_value(self, key: str) -> None:
        """Delete context value of given key

        Args:
            key (str): The key in context which you want to delete
        """
        if hasattr(self.__thread_local_data, "data"):
            self.__thread_local_data.data.pop(key)
        self._serialize_data()

    def clean(self):
        """Clean all data in context"""
        self.__thread_local_data.data = {}
        self._serialize_data()

    def get_all_values(self) -> Dict[str, Any]:
        """Get all values in context

        Returns:
            Dict[str, Any]: A dict as same as context data
        """
        if not hasattr(self.__thread_local_data, "data"):
            return {}
        return copy.copy(self.__thread_local_data.data)

    def __str__(self) -> str:
        if not hasattr(self.__thread_local_data, "serialized_data"):
            return "{}"
        return self.__thread_local_data.serialized_data
