from dataclasses import dataclass
from typing import Type

from datek_jaipur.application.adapters.base import BaseAdapter
from datek_jaipur.domain.compound_types.game import Game


@dataclass
class Scope:
    adapter_class: Type[BaseAdapter]
    game: Game = None
