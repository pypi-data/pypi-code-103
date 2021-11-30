from random import randint

from datek_jaipur.domain.compound_types.goods import GoodsType

CARD_AMOUNTS = {
    GoodsType.DIAMOND: 6,
    GoodsType.GOLD: 6,
    GoodsType.SILVER: 6,
    GoodsType.SPICE: 8,
    GoodsType.CLOTH: 8,
    GoodsType.LEATHER: 10,
    GoodsType.CAMEL: 11,
}


COIN_COLLECTION = {
    GoodsType.DIAMOND: (7, 7, 5, 5, 5),
    GoodsType.GOLD: (6, 6, 5, 5, 5),
    GoodsType.SILVER: (5, 5, 5, 5, 5),
    GoodsType.CLOTH: (5, 3, 3, 2, 2, 1, 1),
    GoodsType.SPICE: (5, 3, 3, 2, 2, 1, 1),
    GoodsType.LEATHER: (4, 3, 2, 1, 1, 1, 1, 1, 1),
}

BONUS_FOR_3_MIN = 1
BONUS_FOR_3_MAX = 3
BONUS_FOR_4_MIN = 4
BONUS_FOR_4_MAX = 6
BONUS_FOR_5_MIN = 7
BONUS_FOR_5_MAX = 9
LARGEST_HERD_BONUS = 5


MULTIPLE_SOLD_BONUS_MAP = {
    3: lambda: randint(BONUS_FOR_3_MIN, BONUS_FOR_3_MAX),
    4: lambda: randint(BONUS_FOR_4_MIN, BONUS_FOR_4_MAX),
    5: lambda: randint(BONUS_FOR_5_MIN, BONUS_FOR_5_MAX),
}

MINIMUM_COIN_TYPES = 4
INITIAL_HAND_SIZE = 5
DECK_SIZE = 5
INITIALLY_NEEDED_CARDS = INITIAL_HAND_SIZE * 2 + DECK_SIZE
INITIAL_SCORE = 0
MAX_CARDS_IN_HAND = 7
