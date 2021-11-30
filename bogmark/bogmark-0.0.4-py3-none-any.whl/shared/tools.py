from enum import Enum


class StrEnum(str, Enum):
    """
    StrEnum subclasses that create variants using `auto()` will have values equal to their names
    Enums inheriting from this class that set values using `enum.auto()` will have variant values equal to their names
    """

    def _generate_next_value_(name, start, count, last_values) -> str:  # noqa
        """
        Uses the name as the automatic value, rather than an integer

        name: the name of the member
        start: the initial start value or None
        count: the number of existing members
        last_value: the last value assigned or None
        """
        return name
