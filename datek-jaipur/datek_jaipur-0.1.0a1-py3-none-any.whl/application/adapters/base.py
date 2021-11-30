from abc import abstractmethod
from typing import Type, Any

from datek_async_fsm.state import BaseState

from datek_jaipur.domain.compound_types.game import Game


class BaseAdapter:
    def __init__(self, state_class: Type[BaseState], game: Game = None):
        self._state_class = state_class
        self._game = game

    @abstractmethod
    async def collect_data(self) -> Any:  # pragma: no cover
        pass
