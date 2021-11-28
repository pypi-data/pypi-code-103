from importlib.resources import Package, Resource, open_text
from typing import cast

from yaml import safe_load

from asking.loaders.loader import Loader
from asking.types import ScriptDict


class YamlResourceLoader(Loader):
    def __init__(self, package: Package, resource: Resource) -> None:
        super().__init__()
        self._package = package
        self._resource = resource

    def load(self) -> ScriptDict:
        with open_text(self._package, self._resource) as r:
            return cast(ScriptDict, safe_load(r))
