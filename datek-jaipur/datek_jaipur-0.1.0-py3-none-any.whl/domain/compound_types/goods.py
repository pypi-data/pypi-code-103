from enum import Enum


class GoodsType(str, Enum):
    DIAMOND = "Diamond"
    GOLD = "Gold"
    SILVER = "Silver"
    CLOTH = "Cloth"
    SPICE = "Spice"
    LEATHER = "Leather"
    CAMEL = "Camel"


GoodsTypeTuple = tuple[GoodsType]
