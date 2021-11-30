from logging import getLogger
from typing import Any, Generic, List, Optional

from doutline.exceptions import LevelTooHighError, NoLevelError
from doutline.types import TData


class OutlineNode(Generic[TData]):
    """
    Node in an outline.

    Arguments:
        level: Hierarchical level under parent. Smaller numbers are higher in
        the hierarchy/towards the root. Larger numbers are lower in the
        hierarchy/towards leaves. `None` implies this is the root.

        data:  Data to assign to this node. `None` implies this is the root.
    """

    def __init__(
        self,
        level: Optional[int] = None,
        data: Optional[TData] = None,
        children: Optional[List["OutlineNode[TData]"]] = None,
    ) -> None:
        self._logger = getLogger("doutline")
        self._data = data
        self._level = level
        self._children = children or []

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OutlineNode):
            self._logger.debug("%s not equal: type mismatch.", self.__class__.__name__)
            return False

        any_other: OutlineNode[Any] = other

        if any_other.level != self.level:
            self._logger.debug(
                "%s not equal: level %s != %s.",
                self.__class__.__name__,
                self.level,
                any_other.level,
            )
            return False

        if any_other.data != self.data:
            self._logger.debug("%s not equal: data mismatch.", self.__class__.__name__)
            return False

        if any_other.children != self.children:
            self._logger.debug(
                "%s not equal: children %s != %s.",
                self.__class__.__name__,
                self.children,
                any_other.children,
            )
            return False

        return True

    def __repr__(self) -> str:
        parts: List[str] = []

        if self.level is not None:
            parts.append(str(self.level))

        if self.data is not None:
            parts.append(f'"{self.data}"')

        if self.children:
            parts.append(f"children={self.children}")

        body = ", ".join(parts)
        return f"{self.__class__.__name__}({body})"

    def append(self, level: int, data: TData) -> None:
        """
        Appends an item to the outline.

        Arguments:
            level: Level to add the item at.
            data:  Item data.

        Raises:
            LevelTooHighError: If the new item is too high in the hierarchy to
            be added to or beneath this node.

            NoLevelError: If a child node without a level index is encountered.
        """

        if self.level is not None and level <= self.level:
            raise LevelTooHighError(self.level, level)

        if not self.children:
            self.children.append(OutlineNode[TData](level=level, data=data))
            return

        last = self.children[-1]

        if last.level is None:
            raise NoLevelError(last)

        if level > last.level:
            last.append(level=level, data=data)
        else:
            self.children.append(OutlineNode[TData](level=level, data=data))

    @property
    def children(self) -> List["OutlineNode[TData]"]:
        return self._children

    @property
    def data(self) -> Optional[TData]:
        """
        Gets the meaningful data associated with this outline item.
        """

        return self._data

    def in_range(self, hi: Optional[int], lo: Optional[int]) -> bool:
        """
        Checks if the node is within the specified range of hierarchical levels.

        If the node has no level then it will not match any range.

        Arguments:
            hi: Highest level to include. `None` implies no upper bound.
            lo: Lowest level to include. `None` implies no lower bound.
        """

        if self.level is None:
            self._logger.debug('Excluding "%s" from range: no level.', self.data)
            return False

        if hi is not None and hi > self.level:
            self._logger.debug(
                'Excluding "%s" from range: level %s < %s.',
                self.data,
                self.level,
                hi,
            )
            return False

        if lo is not None and lo < self.level:
            return False

        return True

    @property
    def level(self) -> Optional[int]:
        return self._level
