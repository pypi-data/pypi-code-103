"""Declares :class:`CanonicalExceptionSchema`."""
import marshmallow
import marshmallow.fields

from .base import BaseSchema


class CanonicalExceptionSchema(BaseSchema, marshmallow.Schema):
    """The schema for exceptions that are not otherwise specified."""
