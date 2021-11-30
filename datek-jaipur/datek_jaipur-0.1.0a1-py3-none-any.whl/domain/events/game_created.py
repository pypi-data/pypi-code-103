from random import sample

from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.compound_types.game import Game, GameCreatedInput
from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.domain.constants import (
    INITIALLY_NEEDED_CARDS,
    INITIAL_HAND_SIZE,
    DECK_SIZE,
    INITIAL_SCORE,
)
from datek_jaipur.domain.errors.game_created import PlayerNamesAreSameError
from datek_jaipur.domain.events.all_card_sets_created import AllCardSetsCreated
from datek_jaipur.domain.events.all_coin_sets_created import AllCoinSetsCreated
from datek_jaipur.domain.events.player_created import PlayerCreated
from datek_jaipur.utils import BaseEvent


class GameCreated(BaseEvent[GameCreatedInput, Game]):
    class Config:
        input_type = GameCreatedInput

    async def _validate(self):
        if self._data_model.player1_name == self._data_model.player2_name:
            raise PlayerNamesAreSameError

    async def _create_result(self) -> Game:
        all_card_created = AllCardSetsCreated()
        await all_card_created.apply()

        initial_cards = sample(list(all_card_created.result), INITIALLY_NEEDED_CARDS)
        hand1 = CardSet(initial_cards[:INITIAL_HAND_SIZE])
        herd1 = hand1.filter_by_type(GoodsType.CAMEL)
        hand2 = CardSet(initial_cards[INITIAL_HAND_SIZE : INITIAL_HAND_SIZE * 2])
        herd2 = hand2.filter_by_type(GoodsType.CAMEL)
        cards_on_deck = CardSet(initial_cards[-DECK_SIZE:])
        cards_in_pack = all_card_created.result - hand1 - hand2 - cards_on_deck

        player_1_created = PlayerCreated(
            name=self._data_model.player1_name,
            goods=hand1 - herd1,
            herd=herd1,
            score=INITIAL_SCORE,
        )
        await player_1_created.apply()

        player_2_created = PlayerCreated(
            name=self._data_model.player2_name,
            goods=hand2 - herd2,
            herd=herd2,
            score=INITIAL_SCORE,
        )
        await player_2_created.apply()

        coins_created = AllCoinSetsCreated()
        await coins_created.apply()

        return Game(
            player1=player_1_created.result,
            player2=player_2_created.result,
            cards_on_deck=cards_on_deck,
            cards_in_pack=cards_in_pack,
            coins=coins_created.result,
            current_player=player_1_created.result,
        )
