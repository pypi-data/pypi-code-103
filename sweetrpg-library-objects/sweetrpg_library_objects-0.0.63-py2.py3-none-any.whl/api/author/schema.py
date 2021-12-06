# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import post_load
from sweetrpg_library_objects.model.author import Author
from sweetrpg_library_objects.utils.user import add_user_info
from sweetrpg_api_core.schema.base import BaseAPISchema


class AuthorAPISchema(BaseAPISchema):
    class Meta:
        type_ = "author"
        self_view = "author_detail"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = "author_list"

    @post_load
    def make_object(self, data, **kwargs):
        data = add_user_info(data)
        return Author(**data)

    id = fields.Str()  # as_string=True, dump_only=True)
    name = fields.Str(required=True)  # required=True) #, load_only=True)
    # volumes = Relationship(
    #     self_view="author_volumes",
    #     self_view_kwargs={"id": "<id>"},
    #     related_view="volume_list",
    #     related_view_kwargs={"author_id": "<id>"},
    #     many=True,
    #     schema="VolumeAPISchema",
    #     type_="volume",
    # )
