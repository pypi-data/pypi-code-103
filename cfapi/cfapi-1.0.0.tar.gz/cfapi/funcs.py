from .contest import Contest
from .problem import Problem
from .profile import Profile

from .exceptions import InvalidURL

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


def from_url(url: str) -> "Union[Contest, Problem, Profile]":
    for t in (Profile, Contest, Problem):
        try:
            return t.from_url(url)
        except InvalidURL:
            pass

    raise InvalidURL(f"URL {url!r} is invalid")
