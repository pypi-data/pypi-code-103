from datek_jaipur.domain.compound_types.card import CardSet
from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.domain.compound_types.player import Player
from datek_jaipur.domain.errors.goods_bought import CardNotOnDeckError
from datek_jaipur.domain.errors.goods_sold import NotEnoughCardsError
from datek_jaipur.domain.errors.goods_traded import (
    NotEnoughResourcesAtPlayerError,
    NotEnoughResourcesOnDeskError,
    GoodsCountsMismatchError,
)
from datek_jaipur.domain.errors.player_created import InvalidNameError

NEW_TURN = "*" * 50


def format_card_set(card_set: CardSet) -> str:
    card_list = card_set.to_list()
    card_list.sort(key=lambda item: item.type)

    return " ".join(_card_format_map[card.type] for card in card_list)


def format_player(player: Player) -> str:
    return player.name


def clear_screen():
    print("\033[2J\033[H")


def print_new_turn():
    print(NEW_TURN)


def format_error(error: Exception) -> str:
    if isinstance(error, InvalidNameError):
        return "Some of the players has invalid name."
    elif isinstance(error, CardNotOnDeckError):
        return f"There is no {error.goods_type} type card on the deck."
    elif isinstance(error, NotEnoughCardsError):
        return f"You don't have enough cards from {error.card_type}"
    elif isinstance(error, NotEnoughResourcesOnDeskError):
        return f"There is not enough from {error.goods_type} on the deck."
    elif isinstance(error, NotEnoughResourcesAtPlayerError):
        return f"You don't have enough cards from {error.goods_type}"
    elif isinstance(error, GoodsCountsMismatchError):
        return f"Invalid number of goods."
    else:
        return error.__class__.__name__


_card_format_map = {
    GoodsType.GOLD: "(G)old",
    GoodsType.DIAMOND: "(D)iamond",
    GoodsType.SILVER: "(Si)lver",
    GoodsType.SPICE: "(Sp)ice",
    GoodsType.LEATHER: "(L)eather",
    GoodsType.CLOTH: "(C)loth",
    GoodsType.CAMEL: "(Ca)mel",
}
