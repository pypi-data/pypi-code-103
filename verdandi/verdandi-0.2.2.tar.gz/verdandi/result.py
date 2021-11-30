from dataclasses import dataclass
from enum import IntEnum
from typing import List


class ResultType(IntEnum):
    OK = 1
    ERROR = 2


@dataclass(eq=True, order=False, frozen=True)
class IterationStats:
    # Time taken in seconds
    duration_sec: float

    # Memory allocated in bytes
    memory_diff: int


@dataclass(eq=False, order=False, frozen=True)
class BenchmarkResult:
    name: str

    rtype: ResultType

    # Time taken in seconds
    duration_sec: float

    # Memory allocated in bytes
    memory_diff: int

    # Captured stream outputs
    stdout: List[str]
    stderr: List[str]

    # Captured exceptions
    exceptions: List[Exception]

    def __str__(self) -> str:
        return f"{self.name} ({self.rtype.name}, duration_sec={self.duration_sec:.4f}, memory_diff={self.memory_diff})"
