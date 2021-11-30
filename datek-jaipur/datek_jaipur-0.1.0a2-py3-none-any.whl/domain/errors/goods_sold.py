from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.errors import EventValidationError


class GoodsSoldValidationError(EventValidationError):
    pass


class NotEnoughCardsError(GoodsSoldValidationError):
    def __init__(self, card_type: GoodsType):
        self.card_type = card_type
