from typing import Any, Dict, Optional, Sequence
from itertools import chain
from pxd_postgres.ltree import LtreeValue
from wcd_geo_db.modules.bank.db import Division, DivisionCode, DivisionTranslation
from wcd_geo_db.modules.code_seeker import CodeSeekerRegistry

from .code_seeker import get_code_seeker_registry
from .code_mapper import CodeMapper
from .dtos import DivisionItem, DivisionTranslationItem
from .merger import MergeCommiter, inject_synonyms


__all__ = (
    'find_by_codes',
    'make_merge_division_code',
    'merge_divisions',
    'merge_division_translations',
)


def get_item_codes(item: DivisionItem):
    return [item['code']] + (item.get('codes') or [])


def find_by_codes(registry: CodeSeekerRegistry, items: Sequence[DivisionItem]) -> CodeMapper:
    codes = [
        (code, registry[code].to_representation(value))
        for item in items
        for code, value in (get_item_codes(item) + (item.get('path') or []))
    ]

    return CodeMapper(
        registry,
        (
            Division.objects.seek_codes(registry=registry, codes=codes)
            |
            # FIXME: This is not the way it should work.
            Division.objects.filter(name__in=[item['name'] for item in items])
        ).distinct()
    )


def make_merge_division_code(seeker, code: Any):
    return seeker.name, code


def update_existing_codes(codes, existing_codes):
    codes_sets = {}

    for code, value in codes:
        codes_sets[code] = codes_sets.get(code) or set(existing_codes.get(code) or [])
        codes_sets[code].add(value)

    for code, items in codes_sets.items():
        existing_codes[code] = list(items)

    return existing_codes


def merge_divisions(
    items: Sequence[DivisionItem],
    change_path: bool = True,
    change_level: bool = True,
    change_types: bool = True,
    should_create: bool = True,
    lookup_on_singular_name_equality=False,
    strict_types_change: bool = False,
):
    d = MergeCommiter(Division, update_fields=(
        ('name', 'types', 'codes', 'level', 'synonyms',)
        +
        (('parent_id', 'path') if change_path else ())
    ))
    # dc = MergeCommiter(DivisionCode, update_fields=('code', 'value'))

    divisions = find_by_codes(get_code_seeker_registry(), items)

    for item in items:
        item_codes = get_item_codes(item)
        eqs = divisions.get_one(item_codes)

        if eqs is None and lookup_on_singular_name_equality:
            eqs = divisions.get_one_by_name(item['name'])

        path = [divisions.get_one([code]) for code in (item['path'] or []) if code]

        if None in path and (change_path or eqs is None):
            d.fail(item, code='path_failure', path=path)
            continue

        path = [(x.id if x else x) for x in path]
        parent_id = path[-1] if len(path) > 0 else None

        if eqs is None:
            if should_create:
                d.create(Division(
                    name = item['name'],
                    codes = update_existing_codes(item_codes, {}),
                    types = item['types'],
                    level = item['level'],
                    path = LtreeValue(path),
                    parent_id=parent_id,
                ))
            else:
                print(item['name'], item['codes'])
        else:
            eqs.path = LtreeValue(path + [eqs.id])
            eqs.codes = update_existing_codes(item_codes, eqs.codes or {})
            eqs.parent_id = parent_id

            if change_level:
                eqs.level = item['level']

            if change_types:
                if strict_types_change:
                    eqs.types = list(item['types'])
                else:
                    eqs.types = list(set((eqs.types or []) + item['types']))

            inject_synonyms(eqs, item['name'])

            d.update(eqs)

    results = d.commit()
    Division.objects.all().update_roughly_invalid_tree()
    Division.objects.filter(pk__in=[x.pk for x in results]).update_relations_from_json()

    d.clear()


def merge_division_translations(
    language: str,
    items: Sequence[DivisionTranslationItem]
):
    creations = []
    updates = []
    merge_failures = []
    entities_founded = find_by_codes(get_code_seeker_registry(), items)
    items_founded = DivisionTranslation.objects.filter(
        language=language, entity_id__in=[
            founded.id
            for founded in
            (entities_founded.get_one(get_item_codes(item)) for item in items)
            if founded is not None
        ]
    )
    map_founded = {item.entity_id: item for item in items_founded}

    for item in items:
        entity = entities_founded.get_one(get_item_codes(item))

        if entity is None:
            merge_failures.append(('no_entity', item))
            continue

        existing = map_founded.get(entity.id)

        if existing is None:
            creations.append(DivisionTranslation(
                language=language,
                name=item['name'],
                synonyms=item.get('synonyms') or '',
                entity_id=entity.id
            ))
        else:
            inject_synonyms(existing, item['name'], item.get('synonyms') or '')
            updates.append(existing)

    print(merge_failures)

    DivisionTranslation.objects.bulk_create(creations, ignore_conflicts=True)
    DivisionTranslation.objects.bulk_update(
        updates, fields=('synonyms',)
    )
