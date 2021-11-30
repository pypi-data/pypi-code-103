from dataclasses import dataclass
from typing import Optional

from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.compound_types.coin import CoinSet
from datek_jaipur.domain.compound_types.player import Player
from datek_jaipur.simple_types import Name


@dataclass(frozen=True)
class Game:
    player1: Player
    player2: Player
    cards_in_pack: CardSet
    cards_on_deck: CardSet
    coins: CoinSet
    current_player: Optional[Player] = None
    winner: Optional[Player] = None


@dataclass
class GameCreatedInput:
    player1_name: Name
    player2_name: Name
