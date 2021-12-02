import logging
import re
import time
from collections import namedtuple
from typing import List, NamedTuple, Optional, Type, Union

import requests
from pydantic.main import BaseModel

from ...client import Session
from ...models import Block, BlockFormat, BlockVersion
from .regex import INLINE_CITATION_BLOCK_REGEX


class LocalMarker(NamedTuple):
    marker: str
    local_path: str
    remote_path: str
    content: Optional[str]

    """
        defining __eq__ and __hash__ is to allow the use of set()
    """

    def __eq__(self, other):
        return self.marker == other.marker

    def __hash__(self):
        return hash(("marker", self.marker))


# TODO move to session - easier to mock
def get_model(session: Session, url: str, model: Type[BaseModel] = BlockVersion):
    block = session.get_model(url, model)
    if not block:
        raise ValueError(f"Could not fetch the block {url}")
    return block


def fetch(url: str):
    resp = requests.get(url)
    if resp.status_code >= 400:
        raise ValueError(resp.content)
    return resp.content
