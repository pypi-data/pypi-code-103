from typing import Protocol

from asking.protocols.state_protocol import StateProtocol


class ActionProtocol(Protocol):
    @property
    def state(self) -> StateProtocol:
        """..."""
