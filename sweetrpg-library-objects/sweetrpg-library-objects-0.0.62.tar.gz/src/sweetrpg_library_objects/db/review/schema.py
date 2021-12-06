# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow import fields, INCLUDE
from sweetrpg_library_objects.model.review import Review
from sweetrpg_model_core.schema.base import BaseSchema


class ReviewSchema(BaseSchema):
    model_class = Review

    title = fields.String(required=True)  # , load_only=True)
    text = fields.String(required=True)  # , load_only=True)
    locale = fields.String(required=True)
    volume = fields.String(required=True)
    tags = fields.List(fields.Dict(keys=fields.String(required=True), values=fields.String()))
