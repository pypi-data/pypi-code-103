from typing import List

from dinject.types import Executor


class BashExecutor(Executor):
    """Bash executor."""

    @property
    def arguments(self) -> List[str]:
        """Shell arguments to execute this Bash script."""
        return ["/usr/bin/env", "bash", "-c", self.script]
