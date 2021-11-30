from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.errors import EventValidationError


class GoodsBoughtValidationError(EventValidationError):
    pass


class TooMuchCardsInHandError(GoodsBoughtValidationError):
    pass


class CardNotOnDeckError(GoodsBoughtValidationError):
    def __init__(self, goods_type: GoodsType):
        self.goods_type = goods_type
