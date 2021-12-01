from typing import TypeVar, List, Union, Any

T = TypeVar("T")


class PagenatedResponse:
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: List[Any]

    def __init__(
        self,
        count: int,
        next: Union[str, None],
        previous: Union[str, None],
    ):
        self.count = count
        self.next = next
        self.previous = previous
