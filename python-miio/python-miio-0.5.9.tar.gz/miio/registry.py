from pathlib import Path
import yaml
import logging
from typing import List

_LOGGER = logging.getLogger(__name__)

class Model:
    name: str
    model: str
    zeroconf: str


class Info:
    name: str
    type: str
    models: List[Model]


class Registry:
    def __init__(self):
        pass

    def parse_manifest(self, file):
        with open(file) as fp:
            try:
                data = yaml.safe_load(fp)
                print(data)
            except Exception as ex:
                _LOGGER.error("Unable to parse yaml file %s: %s", file, ex)

    def load_manifests(self):
        integrations = Path(__file__).parent.glob("integrations/**/*.yaml")
        for int in integrations:
            self.parse_manifest(int)


def test_load_manifests():
    r = Registry()
    r.load_manifests()