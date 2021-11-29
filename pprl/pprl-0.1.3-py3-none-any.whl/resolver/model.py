from dataclasses import dataclass, field
from typing import List

from ..encoder import EncoderConfig


@dataclass(frozen=True)
class MPIConfig:
    """
    Represents pseudonyms in a special domain so that they may be resolved to their original identifiers.
    """
    domain: str
    pseudonyms: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResolveRequest:
    """
    Represents a request to resolve and submit pseudonyms to a broker service.
    """
    mpi_config: MPIConfig = field(default_factory=MPIConfig)
    encoder_config: EncoderConfig = field(default_factory=EncoderConfig)
    attribute_list: List[str] = field(default_factory=lambda: ["birth_date", "first_name", "last_name", "gender"])


@dataclass(frozen=True)
class PseudonymMatch:
    """
    Represents a match returned by a pseudonym resolver service.
    """
    pseudonym: str
    confidence: float
