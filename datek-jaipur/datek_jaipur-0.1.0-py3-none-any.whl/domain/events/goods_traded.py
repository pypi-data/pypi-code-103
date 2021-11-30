from collections import Counter
from typing import Generator

from datek_jaipur.domain.compound_types.card import CardSet, Card
from datek_jaipur.domain.compound_types.game import Game
from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.domain.compound_types.player import Player
from datek_jaipur.domain.compound_types.turn import GoodsTradedInput
from datek_jaipur.domain.errors.goods_traded import (
    NotEnoughResourcesAtPlayerError,
    NotEnoughResourcesOnDeskError,
    GoodsCountsMismatchError,
)
from datek_jaipur.utils import BaseEvent, Result


class GoodsTraded(BaseEvent[GoodsTradedInput, Game]):
    class Config:
        input_type = GoodsTradedInput

    async def _validate(self):
        if len(self._data_model.goods_to_acquire) != len(
            self._data_model.goods_to_give_away
        ) or not len(self._data_model.goods_to_acquire):
            raise GoodsCountsMismatchError

        give_away_counts = Counter(self._data_model.goods_to_give_away)

        available_resources_generator = (
            item.type
            for item in self._data_model.game.current_player.goods
            + self._data_model.game.current_player.herd
        )

        available_resources = Counter(available_resources_generator)

        for goods_type, count in give_away_counts.items():
            if available_resources.get(goods_type, -1) < count:
                raise NotEnoughResourcesAtPlayerError(goods_type)

        resources_on_deck_generator = (
            item.type for item in self._data_model.game.cards_on_deck
        )

        acquire_counts = Counter(self._data_model.goods_to_acquire)
        resources_on_deck = Counter(resources_on_deck_generator)

        for goods_type, count in acquire_counts.items():
            if resources_on_deck.get(goods_type, -1) < count:
                raise NotEnoughResourcesOnDeskError(goods_type)

    async def _create_result(self) -> Result:
        cards_to_pick = CardSet(card for card in self._get_cards_to_pick())
        cards_to_throw = CardSet(card for card in self._get_cards_to_throw())
        herd = cards_to_pick.filter_by_type(GoodsType.CAMEL)
        goods = cards_to_pick - herd

        new_player = Player(
            name=self._data_model.game.current_player.name,
            score=self._data_model.game.current_player.score,
            goods=self._data_model.game.current_player.goods - cards_to_throw + goods,
            herd=self._data_model.game.current_player.herd - cards_to_throw + herd,
        )

        if self._data_model.game.player1 == self._data_model.game.current_player:
            player1 = new_player
            player2 = self._data_model.game.player2
            current_player = player2
        else:
            player1 = self._data_model.game.player1
            player2 = new_player
            current_player = player1

        return Game(
            player1=player1,
            player2=player2,
            cards_in_pack=self._data_model.game.cards_in_pack,
            cards_on_deck=self._data_model.game.cards_on_deck
            - cards_to_pick
            + cards_to_throw,
            coins=self._data_model.game.coins,
            current_player=current_player,
        )

    def _get_cards_to_pick(self) -> Generator[Card, None, None]:
        source_cards = CardSet(self._data_model.game.cards_on_deck)
        for goods_type in self._data_model.goods_to_acquire:
            for card in source_cards:
                if card.type == goods_type:
                    yield card
                    source_cards -= card

    def _get_cards_to_throw(self) -> Generator[Card, None, None]:
        source_cards = (
            self._data_model.game.current_player.goods
            + self._data_model.game.current_player.herd
        )
        for goods_type in self._data_model.goods_to_give_away:
            for card in source_cards:
                if card.type == goods_type:
                    yield card
                    source_cards -= card
