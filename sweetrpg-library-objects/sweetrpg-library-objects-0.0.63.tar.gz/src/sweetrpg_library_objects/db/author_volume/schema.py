# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow import fields
from sweetrpg_library_objects.model.author import Author
from sweetrpg_model_core.schema.base import BaseSchema


class AuthorSchema(BaseSchema):
    model_class = Author

    name = fields.Str(required=True)  # , load_only=True)
    volumes = fields.List(fields.Str())
