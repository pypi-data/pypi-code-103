from abc import ABC, abstractmethod
from typing import Optional


class WorkFlowStep(ABC):
    """Abstract class used to define the base of a WorkFlowStep."""

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def dest_table(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def upstream(self) -> Optional[str]:
        raise NotImplementedError()
