from __future__ import annotations

import abc
from typing import Any, Optional

"""
Item interface. This interface represents common properties of structured
data. Supported item kinds are nodes, attributes and values.
The item content if a tuple of (name, value, namespace) information, where name
is mandatory and value and namespace are optional.
It might be extended by the sub implementations.
"""


class DrbItem(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Returns the name of the item. This name does not contains
        any prefix, path nor any other location or identification part.
        :return: The name of the item.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def namespace_uri(self) -> Optional[str]:
        """
        Get namespace URI. The namespace URI of this item. This is not a
        computed value that is the result of a namespace lookup based on an
        examination of the namespace declarations in scope.
        It is merely the namespace URI given at creation time.

        :return: The namespace URI or null if unspecified.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def value(self) -> Optional[Any]:
        """
        The value of the item.
        :return: value of any type
        """
        raise NotImplementedError
