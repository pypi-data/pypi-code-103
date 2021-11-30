from typing import Optional

from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.compound_types.coin import CoinSet
from datek_jaipur.domain.compound_types.player import Player
from datek_jaipur.domain.constants import DECK_SIZE, MINIMUM_COIN_TYPES


def get_herd_master(player1: Player, player2: Player) -> Optional[Player]:
    player1_herd_size = len(player1.herd)
    player2_herd_size = len(player2.herd)

    if player1_herd_size > player2_herd_size:
        return player1
    elif player2_herd_size > player1_herd_size:
        return player2


def get_winner(player1: Player, player2: Player) -> Optional[Player]:
    if player1.score > player2.score:
        return player1
    elif player2.score > player1.score:
        return player2


def is_game_ended(remaining_coins: CoinSet, cards_on_deck: CardSet):
    return (
        len(cards_on_deck) < DECK_SIZE
        or remaining_coins.type_count() < MINIMUM_COIN_TYPES
    )
