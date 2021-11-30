from enum import Enum

from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.domain.events.goods_bought import GoodsBought
from datek_jaipur.domain.events.goods_sold import GoodsSold
from datek_jaipur.domain.events.goods_traded import GoodsTraded


class AcceptLowerNameMixin:
    @classmethod
    def _missing_(cls, value):
        for item in cls:
            if item.name.lower() == value.lower():
                return item


class TurnType(AcceptLowerNameMixin, Enum):
    S = GoodsSold
    B = GoodsBought
    T = GoodsTraded


turn_prompt = {
    TurnType.S: "Pick something to sell: ",
    TurnType.B: "Pick something to buy: ",
}


class ConsoleGoodsType(AcceptLowerNameMixin, Enum):
    D = GoodsType.DIAMOND
    G = GoodsType.GOLD
    SP = GoodsType.SPICE
    SI = GoodsType.SILVER
    L = GoodsType.LEATHER
    C = GoodsType.CLOTH
    CA = GoodsType.CAMEL


class PlayAgainAnswer(AcceptLowerNameMixin, Enum):
    Y = "Yes"
    N = "No"
