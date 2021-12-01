
from enum import Enum

from hardcode_house_model.house.common import (HouseLocation, HouseProperty,
                                               HouseQuotation,
                                               TransactionProperty)
from hardcode_house_model.util.mongo_mixin import DocumentMixin, MongoMixin
from mongo_driver import Document, EmbeddedDocument
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 ListField, StringField, URLField)


class SpiderArguments(EmbeddedDocument, MongoMixin):
    city = StringField()

class SpiderJob(Document, MongoMixin):
    class Status(Enum):
        Running = 0
        Completed = 100

    class SpiderRunEnv(Enum):
        Zyte = "Zyte"
        Scrapyd = "Scrapyd"

    meta = {
        "strict": False,
        "indexes": [
            {"fields": ("spider", "job"), "unique": True},
            ("job", "spider_run_env"),
            ("status", "spider_run_env"),
            ("arguments.city"),
            ("updated_datetime")
        ]
    }

    spider = StringField(required=True)
    job = StringField(required=True)
    spider_run_env = StringField(required=True)
    status = IntField(required=True)
    item_count = IntField(required=True)
    arguments = EmbeddedDocumentField(SpiderArguments)
    updated_datetime = DateTimeField(required=True)
