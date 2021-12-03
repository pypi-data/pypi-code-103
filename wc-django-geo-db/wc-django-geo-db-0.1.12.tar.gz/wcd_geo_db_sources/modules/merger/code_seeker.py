from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Type
from django.utils.module_loading import import_string
from django.db import models
from wcd_geo_db.modules.code_seeker import CodeSeekerRegistry
from .dtos import CodesItem


__all__ = 'get_code_seeker_registry', 'CodesResolver',


def get_code_seeker_registry() -> CodeSeekerRegistry:
    from wcd_geo_db_sources.conf import settings

    if settings.SOURCE_MERGE_CODE_SEEKER_REGISTRY:
        return import_string(settings.SOURCE_MERGE_CODE_SEEKER_REGISTRY)

    return None


def code_collector(item: CodesItem):
    return [item['code']] + (item.get('codes') or [])


class CodesResolver:
    items: Sequence[models.Model]
    items_map: Dict[Any, models.Model]
    registry: CodeSeekerRegistry
    codes: Sequence[models.Model]
    codes_map: Dict[Tuple[str, str], models.Model]
    code_collector: Callable

    def __init__(
        self,
        registry: CodeSeekerRegistry,
        model: Type[models.Model],
        code_collector = code_collector,
        code_model: Optional[Type[models.Model]] = None
    ):
        self.registry = registry
        self.model = model
        self.code_collector = code_collector
        self.code_model = code_model or self.model._meta.get_field('codes_set').through

    def find_codes(self, items: Sequence[CodesItem]):
        q = models.Q()
        codes = (
            (code, self.registry[code].to_value(value))
            for item in items
            for code, value in self.code_collector(item)
        )

        for code, value in codes:
            q |= models.Q(code=code, value=value)

        return self.code_model.objects.filter(q)

    def find(self, items: Sequence[CodesItem]) -> 'CodesResolver':
        self.codes = self.find_codes(items)
        self.codes_map = {code.entity_id: code for code in self.codes}
        self.items = self.model.objects.filter(id__in={x.entity_id for x in self.codes})

        return self

    def prepare_mapping(self):
        mapping = self.mapping

        for item in self.items:
            for code, value in item.codes.items():
                mapping[code] = mapping.get(code) or []
                mapping[code].append((value, item))

    def get_by_codes(self, codes: Sequence):
        r = self.registry

        return (
            item
            for code, value in codes
            for stored_value, item in (self.mapping.get(code) or [])
            if (
                # code in self.registry and
                self.registry[code].eq(value, stored_value)
            )
        )

    def get_one(self, codes: Sequence) -> models.Model:
        return next(self.get_by_codes(codes), None)
