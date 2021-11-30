from typing import Optional

from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.compound_types.coin import CoinSet
from datek_jaipur.domain.compound_types.game import Game
from datek_jaipur.domain.compound_types.player import Player
from datek_jaipur.domain.compound_types.turn import GoodsSoldEventInput
from datek_jaipur.domain.constants import MULTIPLE_SOLD_BONUS_MAP, LARGEST_HERD_BONUS
from datek_jaipur.domain.errors.goods_sold import NotEnoughCardsError
from datek_jaipur.domain.utils import is_game_ended, get_herd_master
from datek_jaipur.simple_types import Amount
from datek_jaipur.utils import BaseEvent


class GoodsSold(BaseEvent[GoodsSoldEventInput, Game]):
    _cards_to_sell: CardSet
    _current_player: Player
    _herd_master: Optional[Player]
    _earned_coins: CoinSet
    _bonus: Amount

    class Config:
        input_type = GoodsSoldEventInput

    async def _validate(self):
        self._cards_to_sell = self._data_model.game.current_player.goods.filter_by_type(
            self._data_model.goods_type
        )

        if len(self._cards_to_sell) < 2:
            raise NotEnoughCardsError(self._data_model.goods_type)

    async def _create_result(self):
        self._earned_coins = self._data_model.game.coins.retrieve(
            type_=self._cards_to_sell.to_list()[0].type,
            amount=len(self._cards_to_sell),
        )
        self._bonus = MULTIPLE_SOLD_BONUS_MAP.get(len(self._cards_to_sell), lambda: 0)()

        self._current_player = self._data_model.game.current_player
        remaining_coins = self._data_model.game.coins - self._earned_coins

        return (
            self._create_result_for_end()
            if is_game_ended(remaining_coins, self._data_model.game.cards_on_deck)
            else self._create_result_for_next_turn()
        )

    def _create_result_for_end(self):
        self._herd_master = get_herd_master(
            self._data_model.game.player1, self._data_model.game.player2
        )

        if self._data_model.game.player1 == self._current_player:
            player1_goods = self._current_player.goods - self._cards_to_sell
            player2_goods = self._data_model.game.player2.goods
        else:
            player1_goods = self._data_model.game.player1.goods
            player2_goods = self._current_player.goods - self._cards_to_sell

        player1 = Player(
            name=self._data_model.game.player1.name,
            score=self._calculate_new_score_for_player(self._data_model.game.player1),
            herd=self._data_model.game.player1.herd,
            goods=player1_goods,
        )

        player2 = Player(
            name=self._data_model.game.player2.name,
            score=self._calculate_new_score_for_player(self._data_model.game.player2),
            herd=self._data_model.game.player2.herd,
            goods=player2_goods,
        )

        winner = player1 if player1.score > player2.score else player2

        return Game(
            player1=player1,
            player2=player2,
            cards_in_pack=self._data_model.game.cards_in_pack,
            cards_on_deck=self._data_model.game.cards_on_deck,
            coins=self._data_model.game.coins - self._earned_coins,
            winner=winner,
        )

    def _calculate_new_score_for_player(self, player: Player) -> Amount:
        herd_bonus = LARGEST_HERD_BONUS if self._herd_master == player else 0
        score = player.score + herd_bonus
        if player != self._current_player:
            return score

        return score + self._earned_coins.value + self._bonus

    def _create_result_for_next_turn(self):
        new_score = self._current_player.score + self._earned_coins.value + self._bonus

        new_player = Player(
            name=self._current_player.name,
            score=new_score,
            goods=self._current_player.goods - self._cards_to_sell,
            herd=self._current_player.herd,
        )

        if self._data_model.game.player1 == self._current_player:
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
            current_player=current_player,
            cards_in_pack=self._data_model.game.cards_in_pack,
            cards_on_deck=self._data_model.game.cards_on_deck,
            coins=self._data_model.game.coins - self._earned_coins,
        )
