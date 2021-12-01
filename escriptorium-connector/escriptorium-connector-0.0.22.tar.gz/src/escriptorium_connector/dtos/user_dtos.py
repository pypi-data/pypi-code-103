from dataclasses import dataclass
from typing import Union, List, Any
from .super_dtos import PagenatedResponse


@dataclass
class GetOnboarding:
    onboarding: bool


@dataclass
class GetUser(PagenatedResponse):
    count: int
    previous: Union[str, None]
    next: Union[str, None]
    results: List[GetOnboarding]

    def __init__(
        self,
        count: int,
        next: Union[str, None],
        previous: Union[str, None],
        results: List[Any] = [],
    ):
        super(GetUser, self).__init__(count, next, previous)
        self.results = [GetOnboarding(**x) for x in results]
