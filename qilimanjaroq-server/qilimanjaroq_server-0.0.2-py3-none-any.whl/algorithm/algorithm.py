# algorithm.py
from abc import ABC, abstractmethod
from typing import Any
from typeguard import typechecked
from qilimanjaroq_server.typings.algorithm import AlgorithmOptions
from qilimanjaroq_server.typings.job import JobBackend


class Algorithm(ABC):
    """ Generic class to handle algorithms

    """

    @typechecked
    def __init__(self, options: AlgorithmOptions, backend: JobBackend) -> None:
        self._options = options
        self._backend = backend

    @abstractmethod
    def execute(self) -> Any:
        pass
