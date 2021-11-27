# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from datetime import datetime
from mongoengine import Document, fields
from pymongo import ASCENDING
from sweetrpg_library_objects.db.author_property.document import AuthorPropertyDocument


class AuthorDocument(Document):
    """A model object representing an RPG author."""

    meta = {
        "indexes": [{"name": "author_name", "fields": ["name"]}],
        "db_alias": "default",
        "collection": "authors",
        "strict": False,
    }

    # basic properties
    name = fields.StringField(min_length=1, max_length=200, required=True)
    properties = fields.ListField(fields.EmbeddedDocumentField(AuthorPropertyDocument))
    tags = fields.ListField(field=fields.ReferenceField("TagDocument"))

    # audit properties
    created_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    created_by = fields.StringField(default="system", required=True)
    updated_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    updated_by = fields.StringField(default="system", required=True)
    deleted_at = fields.DateTimeField(null=True)
    deleted_by = fields.StringField(null=True)
