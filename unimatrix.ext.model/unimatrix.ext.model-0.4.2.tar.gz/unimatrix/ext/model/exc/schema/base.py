"""Declares :class:`BaseSchema`."""
import marshmallow.fields


class BaseSchema:
    id = marshmallow.fields.UUID(
        required=True
    )

    code = marshmallow.fields.String(
        required=True
    )

    message = marshmallow.fields.String(
        required=True
    )

    detail = marshmallow.fields.String(
        required=False
    )

    hint = marshmallow.fields.String(
        required=False
    )
