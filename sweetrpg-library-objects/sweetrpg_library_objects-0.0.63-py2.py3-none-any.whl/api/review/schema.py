# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sweetrpg_library_objects.model.review import Review
from sweetrpg_api_core.schema.base import BaseAPISchema


class ReviewAPISchema(BaseAPISchema):
    model_class = Review

    class Meta:
        type_ = "review"
        self_view = "review_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "review_list"

    title = fields.String(required=True)  # , load_only=True)
    text = fields.String(required=True)  # , load_only=True)
    locale = fields.String(required=True, default="en_US")
    volume = Relationship(attribute='volume',
                          self_view='review_volume',
                          self_view_kwargs={'id': '<id>'},
                          related_view='volume_detail',
                          related_view_kwargs={'volume_id': '<id>'},
                          schema='VolumeAPISchema',
                          type_='volume')
    tags = Relationship(self_view='review_tags',
                        self_view_kwargs={'id': '<id>'},
                        related_view='tag_list',
                        related_view_kwargs={'id': '<id>'},
                        many=True,
                        schema='TagAPISchema',
                        type_='tag',
                        id_field='tag_id')
