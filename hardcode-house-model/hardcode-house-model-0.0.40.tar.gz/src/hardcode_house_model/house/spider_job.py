
from enum import Enum

from hardcode_house_model.house.base import MONGO_DB_NAME
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
        "db_name": MONGO_DB_NAME,
        "allow_inheritance": False,
        "indexes": [
            {"keys": "spider:1,job:1", "unique": True},
            {"keys": "job:1,spider_run_env:1"},
            {"keys": "status:1,spider_run_env:1"},
            {"keys": "arguments.city:1"},
            {"keys": "updated_datetime:1"}
        ]
    }

    spider = StringField(required=True)
    job = StringField(required=True)
    spider_run_env = StringField(required=True)
    status = IntField(required=True)
    item_count = IntField(required=True)
    arguments = EmbeddedDocumentField(SpiderArguments)
    updated_datetime = DateTimeField(required=True)
