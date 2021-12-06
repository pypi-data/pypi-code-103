from datetime import datetime
from typing import Any, Optional, Type, Union

from tortoise import fields
from tortoise.fields import DatetimeField
from tortoise.fields.relational import ManyToManyRelation
from tortoise.models import Model

from .. import json


class LocalDatetimeField(DatetimeField):
    def to_db_value(
        self, value: Optional[datetime], instance: Union[Type[Model], Model]
    ) -> Optional[datetime]:
        value = super().to_db_value(value, instance)
        if (
            value
            and value.tzinfo is not None
            and value.tzinfo.utcoffset(value) is not None
        ):
            value = value.astimezone()
        return value


def JSONField(**kwargs: Any) -> fields.JSONField:
    return fields.JSONField(encoder=json.fast_dumps, decoder=json.loads, **kwargs)


def ManyToManyField(
    model_name: str,
    through: Optional[str] = None,
    forward_key: Optional[str] = None,
    backward_key: str = "",
    related_name: str = "",
    on_delete: str = fields.CASCADE,
    db_constraint: bool = True,
    **kwargs: Any,
) -> ManyToManyRelation[Any]:
    return fields.ManyToManyField(  # type: ignore
        model_name=model_name,
        through=through,
        forward_key=forward_key,
        backward_key=backward_key,
        related_name=related_name,
        on_delete=on_delete,
        db_constraint=db_constraint,
        **kwargs,
    )
