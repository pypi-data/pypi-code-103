from typing import Any, Dict, Optional, Sequence, Tuple
from django.db import models
from wcd_geo_db.modules.code_seeker import CodeSeekerRegistry


__all__ = 'CodeMapper',


class CodeMapper:
    items: Sequence[models.Model]
    registry: CodeSeekerRegistry
    mapping: Dict[str, Sequence[Tuple[Any, models.Model]]]

    def __init__(self, registry: CodeSeekerRegistry, items):
        self.items = items
        self.registry = registry
        self.mapping = {}
        self.name_groups = {}

        self.prepare_mapping()

    def prepare_mapping(self):
        mapping = self.mapping

        for item in self.items:
            for code, values in item.codes.items():
                for value in values:
                    mapping[code] = mapping.get(code) or []
                    mapping[code].append((value, item))

            self.name_groups[item.name] = self.name_groups.get(item.name) or []
            self.name_groups[item.name].append(item)

    def get_by_codes(self, codes: Sequence):
        r = self.registry

        return (
            item
            for code, value in codes
            for stored_value, item in (self.mapping.get(code) or [])
            if (
                # code in self.registry and
                r[code].eq(
                    r[code].to_representation(value),
                    r[code].to_representation(stored_value)
                )
            )
        )

    def get_one(self, codes: Sequence) -> Optional[models.Model]:
        return next(self.get_by_codes(codes), None)

    def get_one_by_name(self, name: str) -> Optional[models.Model]:
        if name in self.name_groups and len(self.name_groups[name]) == 1:
            return self.name_groups[name][0]

        return None
