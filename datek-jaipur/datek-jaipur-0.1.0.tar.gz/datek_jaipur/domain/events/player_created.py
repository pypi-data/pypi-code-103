from datek_jaipur.domain.compound_types.player import Player, PlayerCreatedEventInput
from datek_jaipur.domain.errors.player_created import InvalidNameError
from datek_jaipur.utils import BaseEvent


class PlayerCreated(BaseEvent[PlayerCreatedEventInput, Player]):
    class Config:
        input_type = PlayerCreatedEventInput

    async def _validate(self):
        self._data_model.name = self._data_model.name.strip()
        if not self._data_model.name:
            raise InvalidNameError

    async def _create_result(self) -> Player:
        return Player(**self._data_model.__dict__)
