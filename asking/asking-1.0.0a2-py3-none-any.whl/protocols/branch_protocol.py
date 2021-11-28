from typing import List, Protocol


class BranchProtocol(Protocol):
    @property
    def response(self) -> List[str]:
        """
        Responses that this branch responds to.
        """

    def is_regex(self, value: str) -> bool:
        """
        Returns `True` if `value` is a regular expression.
        """
