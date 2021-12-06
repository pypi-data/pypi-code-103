# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from mongoengine import EmbeddedDocument, fields
from pymongo import ASCENDING


class AuthorPropertyDocument(EmbeddedDocument):
    """A mapping object for author properties."""

    meta = {
        "indexes": [{"name": "author_property_name", "fields": ["name"]}],
        "db_alias": "default",
        "collection": "author_properties",
        "strict": False,
    }

    # basic properties
    name = fields.StringField(min_length=1, max_length=50, required=True)
    value = fields.StringField(min_length=2, max_length=200, required=True)
    kind = fields.StringField(min_length=1, max_length=20, required=True)
