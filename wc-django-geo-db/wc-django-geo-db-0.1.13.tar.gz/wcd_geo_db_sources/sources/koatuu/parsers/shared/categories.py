from enum import Enum


__all__ = 'Category', 'CATEGORY_ALIASES', 'get_category'


class Category(str, Enum):
    CITY = chr(1052)
    CITY_DISTRICT = chr(1056)
    TOWN = chr(1058)
    VILLAGE = chr(1057)
    HAMLET = chr(1065)


CATEGORY_ALIASES = {
    chr(67): Category.VILLAGE,
}


def get_category(c: str):
    if c in CATEGORY_ALIASES:
        c = CATEGORY_ALIASES[c]

    if c in Category._value2member_map_:
        return Category(c)

    return None
