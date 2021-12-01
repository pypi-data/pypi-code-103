from dataclasses import dataclass, field
from typing import Dict

from ..match import MatchConfig


@dataclass(frozen=True)
class SessionResponse:
    """
    Represents a response from a broker session after a session has been successfully created.
    """
    secret: str
    extra_headers: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BrokerMatch:
    """
    Represents a match returned by the broker.
    """
    bit_vector: str
    confidence: float


@dataclass(frozen=True)
class SessionCancellation:
    """
    Represents a cancellation method which may be included in a session creation request.
    """
    method: str
    options: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionRequest:
    """
    Represents a session creation request.
    """
    match_config: MatchConfig = field(default_factory=MatchConfig)
    session_cancellation: SessionCancellation = field(default_factory=SessionCancellation)
