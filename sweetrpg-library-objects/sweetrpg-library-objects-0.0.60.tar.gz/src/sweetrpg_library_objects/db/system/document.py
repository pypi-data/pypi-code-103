# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from datetime import datetime
from mongoengine import Document, fields


class SystemDocument(Document):
    """A mapping object to convert MongoDB data to a System object."""

    meta = {
        "indexes": [
            {"name": "system_name", "fields": ["name"]},
        ],
        "db_alias": "default",
        "collection": "systems",
        "strict": False,
    }

    # basic properties
    name = fields.StringField(required=True)

    # relations
    volumes = fields.ListField(field=fields.ReferenceField("VolumeDocument"))
    tags = fields.ListField(field=fields.ReferenceField("TagDocument"))

    # audit properties
    created_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    created_by = fields.StringField(default="system", required=True)
    updated_at = fields.DateTimeField(default=datetime.utcnow, required=True)
    updated_by = fields.StringField(default="system", required=True)
    deleted_at = fields.DateTimeField(null=True)
    deleted_by = fields.StringField(default="system", required=True)
