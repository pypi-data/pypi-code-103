from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, TypedDict
from functools import partial
import json
from pprint import pprint
from collections import deque
from enum import Enum
from itertools import chain
from fuzzywuzzy import fuzz
from wcd_geo_db_sources.sources.koatuu.parsers.shared.categories import Category
from wcd_geo_db_sources.sources.koatuu.parsers.shared.postprocess import postprocess_items

from ..koatuu.parsers.shared import Geo, collect_hierarchy, Hierarchy


MIN_MATCH_RATIO = 84
STRICT_MATCH_RATIO = 1000
VILLAGE_MATCH_RATIO = 98
MIN_TRULY_MATCH_RATIO = 94
MAX_PASS = 2
VILLAGE_PREFIXES = (
    (chr(99) + '.', Category.VILLAGE),
    (chr(1089) + '.', Category.VILLAGE),
    (chr(99) + '-', Category.VILLAGE),
    (chr(1089) + '-', Category.VILLAGE),
    (f'{chr(99)}-щ{chr(101)} ', Category.HAMLET),
    (f'{chr(1089)}-щ{chr(101)} ', Category.HAMLET),
    (f'{chr(99)}-щ{chr(1077)} ', Category.HAMLET),
    (f'{chr(1089)}-щ{chr(1077)} ', Category.HAMLET),
)
CHARS_MATCH = 100.0 / (100 - MIN_TRULY_MATCH_RATIO)
NEW_TO_OLD_COMPARISON_ERROR = 1.05
MIN_KOATUU_STRAING_COMPARISON_RATING = 5
KOATUU_MATCH_RATIO = 94


class MissType(str, Enum):
    NEW = 'new'
    OLD = 'old'


class DiffItem(TypedDict):
    items: List[Geo]
    codes: Set[str]


class Missing(TypedDict):
    key: str
    type: MissType


class Diff(TypedDict):
    codes_map: Dict[str, str]
    items: Dict[str, DiffItem]


GeoList = List[Geo]
GeoMap = Dict[str, Geo]
Founded = Tuple[int, int, int, str, Geo]


class PossibilitiesItem(TypedDict):
    miss: Missing
    geo: Geo
    possibilities: List[Founded]


Possibilities = Dict[str, PossibilitiesItem]


def make_geo_map(items: GeoList) -> GeoMap:
    return {item['code'][1]: item for item in items}


def find_missing(older: GeoMap, newer: GeoMap) -> List[Missing]:
    older_set = set(older.keys())
    newer_set = set(newer.keys())

    return list(chain(
        ({'key': key, 'type': MissType.NEW} for key in older_set - newer_set),
        ({'key': key, 'type': MissType.OLD} for key in newer_set - older_set),
    ))


def find_existing_parent(
    missing: Geo,
    hierarchy: Hierarchy,
    should_pass: int = 0
) -> Tuple[int, Geo]:
    for index, (code, parent) in enumerate(reversed(missing['path'] + [missing['code']])):
        if parent in hierarchy:
            if should_pass <= 0:
                return index, parent

            should_pass -= 1

    return 0, None


def eq_municipality_against_its_village_v1(one: str, two: str) -> Tuple[bool, str]:
    for prefix, category in VILLAGE_PREFIXES:
        if one.endswith(prefix + two):
            return True, category

    return False, None


def get_ratio(one: str, two: str) -> int:
    ratio = fuzz.ratio(one, two)

    return ratio


def get_char_matched_ratio(one: str, two: str) -> int:
    # TODO: Fix ratio somehow for a smaller misspels
    ratio = get_ratio(one, two)
    l = min((len(one), len(two)))
    chars = int(CHARS_MATCH * NEW_TO_OLD_COMPARISON_ERROR)

    if l >= chars:
        return ratio

    appendix = '0' * (chars - l)
    new_ratio = get_ratio(one + appendix, two + appendix)

    return new_ratio


def find_possible_equality(
    missing: Geo,
    map: GeoMap,
    hierarchy: Hierarchy,
    should_pass: int = 0,
    ratio_resolver: Callable = get_ratio,
    additional_checkers: List[Callable] = [],
) -> Sequence[Founded]:
    index, parent = find_existing_parent(missing, hierarchy, should_pass=should_pass)

    if parent is None:
        return []

    lookuper = deque([(0, parent)])
    founded = []

    while len(lookuper) > 0:
        depth, code = lookuper.popleft()

        if code in hierarchy:
            for child in hierarchy[code]:
                lookuper.append((depth + 1, child))

        match = None

        if code in map and depth > 0:
            f = missing['name'].lower()
            s = map[code]['name'].lower()

            if f == s:
                match = (STRICT_MATCH_RATIO, index, depth, code, map[code])

            if match is None:
                do, category = eq_municipality_against_its_village_v1(f, s)

                # FIXME: Has a doubt that we need to search for a
                # municipality for a village.
                # Village for municipality would be enough.
                # if not do:
                #     do, category = eq_village_against_its_municipality_v1(s, f)

                if do:
                    if missing['category'] is None:
                        missing['category'] = category
                    elif map[code]['category'] is None:
                        map[code]['category'] = category

                    if missing['category'] == map[code]['category']:
                        match = (VILLAGE_MATCH_RATIO, index, depth, code, map[code])

            if match is None:
                ratio = ratio_resolver(f, s)

                if ratio > MIN_MATCH_RATIO:
                    match = (ratio, index, depth, code, map[code])

            for checker in additional_checkers:
                if match is not None:
                    break

                match = checker(
                    index=index, depth=depth,
                    first_geo=missing,
                    first_name=f,
                    second_code=code,
                    second_geo=map[code],
                    second_name=s,
                )

        if match is not None:
            founded.append(match)

    if len(founded) == 0 and should_pass < MAX_PASS:
        return find_possible_equality(
            missing, map, hierarchy,
            ratio_resolver=ratio_resolver,
            should_pass=should_pass+1,
            additional_checkers=additional_checkers,
        )

    return list(reversed(sorted(founded)))


def resolve_possibilities(
    items: Sequence[Founded],
    min_match_ratio: int = MIN_TRULY_MATCH_RATIO
) -> Sequence[Founded]:
    if len(items) == 0:
        return []

    if items[0][0] == STRICT_MATCH_RATIO:
        return [items[0]]

    return [i for i in items if i[0] >= min_match_ratio]


def find_possibilities(
    missing: List[Missing],
    older: GeoList,
    older_map: GeoMap,
    newer: GeoList,
    newer_map: GeoMap,
    ratio_resolver: Callable = get_ratio,
    additional_checkers: List[Callable] = [],
) -> Possibilities:
    newer_hierarchy = collect_hierarchy(newer)
    older_hierarchy = collect_hierarchy(older)
    possibilities = {}

    for item in missing:
        possibles = []
        geo = None

        if item['type'] == MissType.NEW:
            geo = older_map[item['key']]
            possibles = find_possible_equality(
                geo, newer_map, newer_hierarchy,
                ratio_resolver=ratio_resolver,
                additional_checkers=additional_checkers,
            )
        if item['type'] == MissType.OLD:
            geo = newer_map[item['key']]
            possibles = find_possible_equality(
                geo, older_map, older_hierarchy,
                ratio_resolver=ratio_resolver,
                additional_checkers=additional_checkers,
            )

        possibles = resolve_possibilities(possibles)

        possibilities[item['key']] = {
            'miss': item,
            'geo': geo,
            'possibilities': possibles
        }

    return possibilities


def koatuu_match_ratio_checker(
    first_geo: Geo, second_geo: Geo,
    index, depth, second_code,
    **kwargs
) -> Optional[Founded]:
    o = -5

    # FIXME: Doesen't work that way
    if first_geo['code'][1][:o] == second_geo['code'][1][:o]:
        print(first_geo, second_geo)
        return (KOATUU_MATCH_RATIO, index, depth, second_code, second_geo)


def match_failed_possibilities_with_themselves(possibilities: Possibilities) -> Possibilities:
    failed = [
        value for value in possibilities.values()
        if len(value['possibilities']) != 1
    ]
    if len(failed) == 0:
        return {}

    older = [value['geo'] for value in failed if value['miss']['type'] == MissType.NEW]
    newer = [value['geo'] for value in failed if value['miss']['type'] == MissType.OLD]
    older_map = make_geo_map(older)
    newer_map = make_geo_map(newer)

    new_possibilities = find_possibilities(
        [f['miss'] for f in failed], older, older_map, newer, newer_map,
        ratio_resolver=get_char_matched_ratio,
        additional_checkers=(
            # koatuu_match_ratio_checker,
        )
    )

    for key, item in new_possibilities.items():
        if len(item['possibilities']) == 1:
            possibilities[key] = item

    return possibilities


def str_cmp_rate(first: str, second: str) -> int:
    for i, ch in enumerate(first):
        if ch != second[i]:
            return i

    return 0


def multiple_possibilities_resolver(possibilities: Possibilities) -> Possibilities:
    for match in possibilities.values():
        p = match['possibilities']
        code = match['miss']['key']

        if len(p) < 2:
            continue

        if p[0][0] > p[1][0]:
            match['possibilities'] = [p[0]]
        else:
            # Searching for the same highest rating items.
            # And comparing their koatuu codes
            same = list(reversed(sorted([
                (str_cmp_rate(code, item[3]), item)
                for item in p
                if item[0] == p[0][0]
            ])))

            if (
                same[0][0] >= MIN_KOATUU_STRAING_COMPARISON_RATING
                and
                same[0][0] > same[1][0]
            ):
                match['possibilities'] = [same[0][1]]
            else:
                match['possibilities'] = []

    return possibilities


def update_diff(diff: Diff, possibilities: Possibilities, is_new: bool = False) -> Diff:
    not_pass = {}

    # FIXME: Don't know whether it's right to not match those who found out
    # to be more than 2 or 3 or any other count because we have already checked
    # the amount of possibilities and it was fine there.
    if not is_new:
        n_diff = update_diff({}, possibilities, is_new=True)
        srt = sorted(n_diff['items'].values(), key=lambda x: len(x['items']), reverse=True)

        for cl in srt:
            if len(cl['items']) > 3:
                maximum = next(iter(sorted(
                    [
                        i for i in
                        (
                            (str_cmp_rate(x, y), x, y)
                            for x in cl['codes']
                            for y in cl['codes']
                        )
                        if i[1] != i[2]
                    ],
                    reverse=True
                )))

                maximum = {maximum[1], maximum[2]}
                result = cl['codes'] - maximum

                for code in maximum:
                    not_pass[code] = not_pass.get(code) or set()
                    not_pass[code].update(result)
            elif len(cl['items']) < 4:
                for code in cl['codes']:
                    if code in not_pass:
                        not_pass[code] -= cl['codes']

    mapping = diff.get('codes_map') or {}
    collections = diff.get('items') or {}

    for p in possibilities.values():
        items = [p['geo']] + [i[4] for i in p['possibilities']]
        codes = {item['code'][1] for item in items}

        for code in list(codes):
            codes -= not_pass.get(code) or set()

        true_one = next((mapping[x] for x in codes if x in mapping), p['geo']['code'][1])

        for code in codes:
            mapping[code] = true_one

        collections[true_one] = collections.get(true_one) or {
            'codes': set(),
            'items': []
        }
        collections[true_one]['codes'] = set(collections[true_one]['codes'])
        # Need to add only those items
        only = codes - collections[true_one]['codes']
        collections[true_one]['codes'] |= codes
        collections[true_one]['items'] += [
            item for item in items if item['code'][1] in only
        ]

    return {'codes_map': mapping, 'items': collections}


def find_diff(older: GeoList, newer: GeoList, current: Diff) -> Tuple[Diff, int]:
    older_map = make_geo_map(older)
    newer_map = make_geo_map(newer)
    missing = find_missing(older_map, newer_map)
    overal = len(missing)

    if overal == 0:
        return current, 0

    possibilities = find_possibilities(
        missing, older, older_map, newer, newer_map,
        ratio_resolver=get_ratio
    )
    possibilities = match_failed_possibilities_with_themselves(possibilities)
    possibilities = multiple_possibilities_resolver(possibilities)

    return update_diff(current, possibilities), overal
