# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from datetime import datetime
from mongoengine import Document, fields
from pymongo import ASCENDING


class AuthorVolumeDocument(Document):
    """A database document object linking author and volume."""

    meta = {
        "indexes": [{"name": "author_volume", "fields": ["author", "volume"]}],
        "db_alias": "default",
        "collection": "author_volumes",
        "strict": False,
    }

    # basic properties
    author = fields.ReferenceField("AuthorDocument")
    volume = fields.ReferenceField("VolumeDocument")
