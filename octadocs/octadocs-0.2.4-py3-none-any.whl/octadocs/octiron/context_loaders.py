import json
from functools import lru_cache
from pathlib import Path

import yaml
from iolanta.convert_dollar_signs import convert_dollar_signs
from octadocs.types import Context


@lru_cache(maxsize=None)
def context_from_json(path: Path) -> Context:
    """Load context.json file and return its content."""
    with path.open('r') as context_file:
        return json.load(context_file)


@lru_cache(maxsize=None)
def context_from_yaml(path: Path) -> Context:
    """Load context.json file and return its content."""
    with path.open('r') as context_file:
        raw_data = yaml.load(context_file, Loader=yaml.SafeLoader)
        return convert_dollar_signs(raw_data)
