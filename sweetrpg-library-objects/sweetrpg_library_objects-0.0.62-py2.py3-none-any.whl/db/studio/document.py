# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from datetime import datetime
from mongoengine import Document, fields
from pymongo import ASCENDING


class StudioDocument(Document):
    """A mapping object to convert MongoDB data to a Studio object."""

    meta = {
        "indexes": [
            {"name": "studio_name", "fields": ["name"]},
        ],
        "db_alias": "default",
        "collection": "studios",
        "strict": False,
    }

    # basic properties
    name = fields.StringField(min_length=1, max_length=200, required=True)

    # relations
    volumes = fields.ListField(field=fields.ReferenceField("VolumeDocument"))
    authors = fields.ListField(field=fields.ReferenceField("AuthorDocument"))
    tags = fields.ListField(field=fields.ReferenceField("TagDocument"))

    # audit properties
    created_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    created_by = fields.StringField(default="system", required=True)
    updated_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    updated_by = fields.StringField(default="system", required=True)
    deleted_at = fields.DateTimeField(null=True)
    deleted_by = fields.StringField(default="system", required=True)
