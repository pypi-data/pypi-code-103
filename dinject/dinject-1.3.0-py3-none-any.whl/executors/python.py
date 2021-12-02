from typing import List

from dinject.types import Executor


class PythonExecutor(Executor):
    """Python executor."""

    @property
    def arguments(self) -> List[str]:
        """Shell arguments to execute this Python script."""
        return ["python", "-c", self.script]
