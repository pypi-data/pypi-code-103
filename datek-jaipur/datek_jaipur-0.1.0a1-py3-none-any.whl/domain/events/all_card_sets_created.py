from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.constants import CARD_AMOUNTS
from datek_jaipur.domain.events.card_set_created import CardSetCreated
from datek_jaipur.utils import BaseEvent


class AllCardSetsCreated(BaseEvent[None, CardSet]):
    async def _create_result(self) -> CardSet:
        card_set_events: list[CardSetCreated] = []

        for type_, amount in CARD_AMOUNTS.items():
            event = CardSetCreated(type=type_, amount=amount)
            await event.apply()
            card_set_events.append(event)

        card_sets = (event.result for event in card_set_events)

        return CardSet((card for card_set in card_sets for card in card_set))
