from enum import Enum


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)

    return wrapper


def enum_to_str(enum_value) -> str:
    if enum_value and isinstance(enum_value, Enum):
        return enum_value.value
    else:
        return enum_value
