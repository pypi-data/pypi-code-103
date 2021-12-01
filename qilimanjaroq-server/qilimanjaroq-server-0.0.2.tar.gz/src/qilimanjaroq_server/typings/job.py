import enum
from typing import NamedTuple


class JobBackend(str, enum.Enum):
    SIMULATOR = 'simulator'
    ANNEALING = 'annealing'
    GATE_BASED = 'gate-based'


class JobRequest(NamedTuple):
    description: str
    backend: JobBackend


class JobResponse(NamedTuple):
    description: str
    result: str
