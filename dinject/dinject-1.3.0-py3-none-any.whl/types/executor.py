from abc import ABC, abstractproperty
from typing import List


class Executor(ABC):
    """
    Base implementation of a machine language executor.

    Arguments:
        script: Script to interpret as this language
    """

    def __init__(self, script: str) -> None:
        self.script = script

    @abstractproperty
    def arguments(self) -> List[str]:
        """Shell arguments to execute this script."""
