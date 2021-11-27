# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sweetrpg_library_objects.model.tag import Tag
from sweetrpg_api_core.schema.base import BaseAPISchema


class TagAPISchema(BaseAPISchema):
    model_class = Tag

    class Meta:
        type_ = "tag"
        self_view = "tag_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "tag_list"

    name = fields.Str(required=True)  # , load_only=True)
    value = fields.Str()
