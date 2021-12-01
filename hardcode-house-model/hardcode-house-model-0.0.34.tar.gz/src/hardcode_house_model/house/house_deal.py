
from hardcode_house_model.house.common import (HouseLocation, HouseProperty,
                                               Transaction,
                                               TransactionProperty)
from hardcode_house_model.util.mongo_mixin import DocumentMixin, MongoMixin
from mongo_driver import Document
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 StringField, ListField)


class HouseDeal(Document, MongoMixin, DocumentMixin):
    platform = StringField(required=True)
    platform_house_id = StringField(required=True)
    platform_title = StringField(required=True)
    platform_description = StringField(required=True)
    total_deal_price = FloatField()                   # 成交总价
    total_listing_price = FloatField()                # 挂牌总价
    unit_deal_price = FloatField()                    # 成交单价
    listing_period = IntField()                       # 成交周期
    price_adjustment_times = IntField()               # 调价次数
    estate_name = StringField()
    images = ListField(StringField())
    scrape_datetime = DateTimeField()
    url = StringField()
    house_property = EmbeddedDocumentField(HouseProperty)
    transaction_property = EmbeddedDocumentField(TransactionProperty)
    transactions = ListField(EmbeddedDocumentField(Transaction, default=[]))
    location = EmbeddedDocumentField(HouseLocation)

    created_datetime = DateTimeField()
    updated_datetime = DateTimeField(required=True)

    def to_dict(self):
        return self.to_dict_default("%Y-%m-%d %H:%M:%S")
