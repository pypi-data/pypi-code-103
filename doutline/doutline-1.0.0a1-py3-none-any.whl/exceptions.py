from typing import Any


class LevelTooHighError(Exception):
    """
    Raised when a requested level is too high to possibly exist as a descendent
    of the item hosting the request.

    Arguments:
        host:      Host level index.
        requested: Requested level index.
    """

    def __init__(self, host: int, requested: int) -> None:
        super().__init__(f"Cannot add a level {requested} node beneath level {host}.")


class NoLevelError(Exception):
    """
    Raised when an outline node has no level index.
    """

    def __init__(self, node: Any) -> None:
        super().__init__(f"{node.__class__.__name__} has no index: {node}")
