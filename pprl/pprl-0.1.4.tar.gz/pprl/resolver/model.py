from dataclasses import dataclass, field
from typing import List

from ..encoder import EncoderConfig


@dataclass(frozen=True)
class ClientConfig:
    """
    Represents a client configuration containing domain-specific data.
    """
    domain: str = ""
    attributes: List[str] = field(default_factory=lambda: ["birth_date", "first_name", "last_name", "gender"])


@dataclass(frozen=True)
class ResolveRequest:
    """
    Represents a request to resolve and submit pseudonyms to a broker service.
    """
    client_config: ClientConfig = field(default_factory=ClientConfig)
    encoder_config: EncoderConfig = field(default_factory=EncoderConfig)
    pseudonyms: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class PseudonymMatch:
    """
    Represents a match returned by a pseudonym resolver service.
    """
    pseudonym: str
    confidence: float
