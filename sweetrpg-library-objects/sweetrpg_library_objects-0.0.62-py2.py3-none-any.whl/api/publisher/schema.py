# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sweetrpg_library_objects.model.publisher import Publisher
from sweetrpg_api_core.schema.base import BaseAPISchema


class PublisherAPISchema(BaseAPISchema):
    model_class = Publisher

    class Meta:
        type_ = "publisher"
        self_view = "publisher_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "publisher_list"

    name = fields.Str(required=True)  # , load_only=True)
