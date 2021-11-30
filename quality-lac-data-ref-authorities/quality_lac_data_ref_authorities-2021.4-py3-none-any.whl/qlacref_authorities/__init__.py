import sys
import json
from pathlib import Path


class __Authorities:
    @property
    def records(self):
        with open(Path(__file__).parent / "records.json", 'rt') as jsonfile:
            return json.load(jsonfile)


sys.modules[__name__] = __Authorities()
