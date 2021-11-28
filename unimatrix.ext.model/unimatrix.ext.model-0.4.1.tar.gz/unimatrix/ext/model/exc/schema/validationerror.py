"""Declares :class:`ValidationErrorSchema`."""
import marshmallow
import marshmallow.fields

from .base import BaseSchema


class ValidationErrorSchema(BaseSchema, marshmallow.Schema):
    """The schema for :class:`unimatrix.ext.model.exc.ValidationError`
    exceptions.
    """

    spec = marshmallow.fields.Dict(
        required=True,
        keys=marshmallow.fields.String(),
        values=marshmallow.fields.List(marshmallow.fields.String)
    )

    index = marshmallow.fields.Integer()

    @marshmallow.post_dump
    def remove_index(self, data, *args, **kwargs):
        if data.get('index') is None:
            data.pop('index')
        return data


class CollectionValidationErrorSchema(BaseSchema, marshmallow.Schema):
    """The schema for :class:`unimatrix.ext.model.exc.CollectionValidationError`
    exceptions.
    """

    items = marshmallow.fields.List(
        marshmallow.fields.Nested(ValidationErrorSchema),
        required=True
    )
