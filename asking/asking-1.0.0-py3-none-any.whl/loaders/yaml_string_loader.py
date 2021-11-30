from yaml import safe_load

from asking.loaders.loader import Loader
from asking.types import ScriptDict


class YamlStringLoader(Loader):
    """
    Loads a script from a YAML string.

    Arguments:
        script: Script as YAML.
    """

    def __init__(self, script: str) -> None:
        super().__init__()
        self._script = script

    def load(self) -> ScriptDict:
        d: ScriptDict = safe_load(self._script)
        return d
