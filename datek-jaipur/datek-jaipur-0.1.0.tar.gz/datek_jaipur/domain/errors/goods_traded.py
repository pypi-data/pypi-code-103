from datek_jaipur.domain.compound_types.goods import GoodsType
from datek_jaipur.errors import EventValidationError


class GoodsTradedValidationError(EventValidationError):
    pass


class GoodsCountsMismatchError(GoodsTradedValidationError):
    pass


class NotEnoughResourcesAtPlayerError(GoodsTradedValidationError):
    def __init__(self, goods_type: GoodsType):
        self.goods_type = goods_type


class NotEnoughResourcesOnDeskError(NotEnoughResourcesAtPlayerError):
    pass
