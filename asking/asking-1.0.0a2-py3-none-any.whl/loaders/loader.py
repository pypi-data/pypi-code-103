from abc import ABC, abstractmethod
from typing import Optional

from asking.types import ScriptDict


class Loader(ABC):
    def __init__(self) -> None:
        self._loaded: Optional[ScriptDict] = None

    @abstractmethod
    def load(self) -> ScriptDict:
        """
        Override to load the script dictionary.
        """

    @property
    def script_dict(self) -> ScriptDict:
        if not self._loaded:
            self._loaded = self.load()
        return self._loaded
