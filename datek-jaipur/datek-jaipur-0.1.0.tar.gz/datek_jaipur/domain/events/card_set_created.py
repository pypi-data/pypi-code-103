from datek_jaipur.domain.compound_types.card import CardSet, Card, CardSetCreatedInput
from datek_jaipur.utils import BaseEvent


class CardSetCreated(BaseEvent[CardSetCreatedInput, CardSet]):
    class Config:
        input_type = CardSetCreatedInput

    async def _create_result(self) -> CardSet:
        return CardSet(
            (
                Card(type=self._data_model.type, id=i)
                for i in range(self._data_model.amount)
            )
        )
