
from hardcode_house_model.house.common import (HouseLocation, HouseProperty,
                                               HouseQuotation,
                                               TransactionProperty)
from hardcode_house_model.util.mongo_mixin import DocumentMixin, MongoMixin
from mongo_driver import Document, EmbeddedDocument
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 ListField, StringField, URLField)


class HousePrice(Document, MongoMixin, DocumentMixin):
    meta = {
        "strict": False,
        "indexes": [
            {"fields": ("platform", "platform_house_id"), "unique": True},
            ("estate_name", "area"),
            ("built_datetime"),
            ("location.city", "location.district")
        ]
    }

    platform = StringField(required=True)
    platform_house_id = StringField(required=True)
    platform_title = StringField(required=True)
    platform_description = StringField(required=True)
    total_price = FloatField(required=True)
    unit_price = FloatField(required=True)
    quotation = EmbeddedDocumentField(HouseQuotation)
    area = FloatField()
    estate_name = StringField()
    built_datetime = DateTimeField()
    images = ListField(StringField())
    scrape_datetime = DateTimeField()
    url = URLField()
    house_property = EmbeddedDocumentField(HouseProperty)
    transaction_property = EmbeddedDocumentField(TransactionProperty)
    location = EmbeddedDocumentField(HouseLocation)

    created_datetime = DateTimeField()
    updated_datetime = DateTimeField(required=True)


class HousePriceHistory(Document, MongoMixin, DocumentMixin):
    meta = {
        "strict": False,
        "indexes": [
            {"fields": ("platform", "platform_house_id",
                        "snapshot_date"), "unique": True},
            ("calendar_year", "calendar_weeknumber", "calendar_weekday"),
            ("location.city", "location.district"),
            ("scrapy_job"),
            ("platform", "location.city", "snapshot_date")
        ]
    }

    platform = StringField(required=True)
    platform_house_id = StringField(required=True)
    snapshot_date = DateTimeField(required=True)
    scrapy_job = StringField()
    calendar_year = IntField()
    calendar_weeknumber = IntField()
    calendar_weekday = IntField()
    total_price = FloatField()
    unit_price = FloatField()
    location = EmbeddedDocumentField(HouseLocation)
    quotation = EmbeddedDocumentField(HouseQuotation)
    area = FloatField()
    estate_name = StringField()
    status = IntField()
    updated_datetime = DateTimeField(required=True)

    def to_dict(self):
        return self.to_dict_default("%Y-%m-%d %H:%M:%S")
