from enum import Enum

from hardcode_house_model.house.base import MONGO_DB_NAME
from hardcode_house_model.house.common import HouseLocation, HouseQuotation
from hardcode_house_model.statistics.common import ChangeDirection
from hardcode_house_model.util.mongo_mixin import DocumentMixin, MongoMixin
from mongo_driver import Document, EmbeddedDocument
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 ListField, StringField, URLField)


class HouseEstateWeeklyReport(Document, MongoMixin, DocumentMixin):
    meta = {
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "city:1,platform:1,week_begin_date:1", "unique": True},
        ]
    }

    city = StringField()
    platform = StringField(required=True)
    week_begin_date = DateTimeField()
    mean_price = FloatField()
    price_percentile25 = FloatField()
    price_percentile50 = FloatField()
    price_percentile75 = FloatField()
    price_percentile80 = FloatField()
    price_percentile90 = FloatField()
    price_percentile95 = FloatField()
    house_count = IntField()
    price_increase_count = IntField()
    price_decrease_count = IntField()
    newlisting_count = IntField()
    delisting_count = IntField()
    unchanged_count = IntField()
    updated_datetime = DateTimeField()

class HouseEstateWeeklyPrice(Document, MongoMixin, DocumentMixin):
    meta = {
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "report_id:1,estate_name:1", "unique": True},
            {"keys": "platform:1,estate_name:1,week_begin_date:1,location.city:1,location.district:1"},
            {"keys": "week_begin_date:1,mean_price:1"}
        ]
    }

    report_id = StringField(required=True)
    platform = StringField(required=True)
    estate_name = StringField()
    location = EmbeddedDocumentField(HouseLocation)
    week_begin_date = DateTimeField()
    mean_price = FloatField()
    price_percentile25 = FloatField()
    price_percentile50 = FloatField()
    price_percentile75 = FloatField()
    price_percentile80 = FloatField()
    price_percentile90 = FloatField()
    price_percentile95 = FloatField()
    house_count = IntField()
    price_increase_count = IntField()
    price_decrease_count = IntField()
    newlisting_count = IntField()
    delisting_count = IntField()
    unchanged_count = IntField()
    updated_datetime = DateTimeField()


class HouseEstateWeeklyPriceChange(Document, MongoMixin, DocumentMixin):
    meta = {
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "report_id:1,platform_house_id:1", "unique": True},
            {"keys": "platform_house_id:1,week_begin_date:1,location.city:1,location.district:1"},
            {"keys": "location.city:1,location.district:1,week_begin_date:1"},
            {"keys": "direction:1,delta.total_price:1"},
            {"keys": "direction:1,delta.unit_price:1"}
        ]
    }

    report_id = StringField(required=True)
    estate_name = StringField()
    location = EmbeddedDocumentField(HouseLocation)
    week_begin_date = DateTimeField()
    platform = StringField()
    platform_house_id = StringField()
    last_week_snapshot_date = DateTimeField()
    last_week_quotation = EmbeddedDocumentField(HouseQuotation)
    current_week_snapshot_date = DateTimeField()
    current_week_quotation = EmbeddedDocumentField(HouseQuotation)
    direction = IntField()
    delta = EmbeddedDocumentField(HouseQuotation)
    delta_percentage = FloatField()
    updated_datetime = DateTimeField()


class HouseEstateMonthlyPrice(Document, MongoMixin, DocumentMixin):
    meta = {
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "estate_name:1,month_begin_date:1,location.city:1,location.district:1", "unique": True},
            {"keys": "location.city:1,location.district:1,month_begin_date:1"},
            {"keys": "month_begin_date:1,mean_price:1"},
        ]
    }

    platform = StringField(required=True)
    estate_name = StringField()
    location = EmbeddedDocumentField(HouseLocation)
    month_begin_date = DateTimeField()
    mean_price = FloatField()
    price_percentile25 = FloatField()
    price_percentile50 = FloatField()
    price_percentile75 = FloatField()
    price_percentile80 = FloatField()
    price_percentile90 = FloatField()
    price_percentile95 = FloatField()
    house_count = IntField()
    updated_datetime = DateTimeField()


class HouseEstateMonthlyPriceChange(Document, MongoMixin, DocumentMixin):
    meta = {
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "platform_house_id:1,month_begin_date:1,location.city:1,location.district:1", "unique": True},
            {"keys": "location.city:1,location.district:1,month_begin_date:1"},
            {"keys": "direction:1,delta.total_price:1"},
            {"keys": "direction:1,delta.unit_price:1"}
        ]
    }
    
    estate_name = StringField()
    location = EmbeddedDocumentField(HouseLocation)
    month_begin_date = DateTimeField()
    platform = StringField(required=True)
    platform_house_id = StringField(required=True)
    last_month_snapshot_date = DateTimeField(required=True)
    last_month_quotation = EmbeddedDocumentField(HouseQuotation)
    current_month_snapshot_date = DateTimeField(required=True)
    current_month_quotation = EmbeddedDocumentField(HouseQuotation)
    direction = IntField()
    delta = EmbeddedDocumentField(HouseQuotation)
    updated_datetime = DateTimeField()
