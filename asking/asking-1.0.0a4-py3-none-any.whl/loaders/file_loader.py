from pathlib import Path
from re import IGNORECASE, match
from typing import cast

from yaml import safe_load

from asking.loaders.loader import Loader
from asking.types import ScriptDict


class FileLoader(Loader):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path

    def load(self) -> ScriptDict:
        is_yaml = match(r"^.*\.y(a?)ml$", self._path.name, IGNORECASE)

        if not is_yaml:
            raise Exception("unknown file type")

        with open(self._path, "r") as f:
            return cast(ScriptDict, safe_load(f))
