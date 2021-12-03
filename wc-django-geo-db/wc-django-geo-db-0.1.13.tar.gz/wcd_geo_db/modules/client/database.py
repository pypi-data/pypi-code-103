from typing import Type
from functools import cached_property
from django.db.models import Model, QuerySet
from django.utils.functional import cached_property
from wcd_geo_db.conf import Settings


__all__ = 'DBClientMixin',


class DBClientMixin:
    settings: Settings
    model: Type[Model]

    _qs: QuerySet = cached_property(
        lambda self: self.model.objects.using(self.root.settings.DB_NAME)
    )
