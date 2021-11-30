from asking.loaders.loader import Loader
from asking.types import ScriptDict


class DictionaryLoader(Loader):
    def __init__(self, script: ScriptDict) -> None:
        super().__init__()
        self._script = script

    def load(self) -> ScriptDict:
        return self._script
