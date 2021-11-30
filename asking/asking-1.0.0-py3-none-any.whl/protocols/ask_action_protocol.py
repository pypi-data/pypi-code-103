from typing import Iterable, Optional

from asking.protocols.action_protocol import ActionProtocol
from asking.protocols.branch_protocol import BranchProtocol


class AskActionProtocol(ActionProtocol):
    @property
    def branches(self) -> Iterable[BranchProtocol]:
        """..."""

    @property
    def key(self) -> Optional[str]:
        """..."""

    @property
    def recall(self) -> bool:
        """..."""
