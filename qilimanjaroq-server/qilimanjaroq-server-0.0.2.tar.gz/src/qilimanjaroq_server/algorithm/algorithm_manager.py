# job_manager.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from qilimanjaroq_server.typings.job import JobBackend
from qilimanjaroq_server.typings.algorithm import AlgorithmOptions


class AlgorithmManager(ABC):
    """
    Abstract class to handle algorithm requests and create the concrete algorithm object.
    Subclasses must implement the creation method.
    """

    def __init__(self, options: AlgorithmOptions) -> None:
        self._options = options

    @abstractmethod
    def factory_method(self, backend: JobBackend):
        """ algorithm internal constructor
        """
        pass

    def execute(self, backend: JobBackend) -> Any:
        """
        Creates the specific algorithm instance and calls its execute method.
        """

        # Call the factory method to create an Algorithm object.
        algorithm = self.factory_method(backend=backend)

        return algorithm.execute()
