from enum import Enum

from hardcode_house_model.house.common import HouseLocation, HouseQuotation
from hardcode_house_model.statistics.common import ChangeDirection
from hardcode_house_model.util.mongo_mixin import DocumentMixin, MongoMixin
from mongo_driver import Document, EmbeddedDocument
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 ListField, StringField, URLField)


class HouseEstateWeeklyReport(Document, MongoMixin, DocumentMixin):
    meta = {
        "strict": False,
        "indexes": [
            {"fields": ("city", "platform", "week_begin_date"), "unique": True},
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
        "strict": False,
        "indexes": [
            {"fields": ("report_id", "estate_name"), "unique": True},
            ("platform", "estate_name", "week_begin_date", "location.city", "location.district"),
            ("week_begin_date", "mean_price")
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
        "strict": False,
        "indexes": [
            {"fields": ("report_id", "platform_house_id"), "unique": True},
            ("platform_house_id", "week_begin_date", "location.city", "location.district"),
            ("location.city", "location.district", "week_begin_date"),
            ("direction", "delta.total_price"),
            ("direction", "delta.unit_price")
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
        "strict": False,
        "indexes": [
            {"fields": ("estate_name", "month_begin_date", "location.city", "location.district"), "unique": True},
            ("location.city", "location.district", "month_begin_date"),
            ("month_begin_date", "mean_price")
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
        "strict": False,
        "indexes": [
            {"fields": ("platform_house_id", "month_begin_date", "location.city", "location.district"), "unique": True},
            ("location.city", "location.district", "month_begin_date"),
            ("direction", "delta.total_price"),
            ("direction", "delta.unit_price")
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
