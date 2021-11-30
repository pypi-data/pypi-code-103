from enum import Enum

from hardcode_house_model.util.mongo_mixin import MongoMixin
from mongo_driver import Document, EmbeddedDocument
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField, IntField,
                                 ListField, StringField, URLField)


class ChangeDirection(Enum):
    Increase = 1
    Decrease = 2
    Newlisting = 3
    Delisting = 4
