from dataclasses import dataclass

from datek_jaipur.domain.compound_types.game import Game
from datek_jaipur.domain.compound_types.goods import GoodsType, GoodsTypeTuple


@dataclass
class GoodsSoldEventInput:
    game: Game
    goods_type: GoodsType


class GoodsBoughtInput(GoodsSoldEventInput):
    pass


@dataclass
class GoodsTradedInput:
    game: Game
    goods_to_give_away: GoodsTypeTuple
    goods_to_acquire: GoodsTypeTuple
