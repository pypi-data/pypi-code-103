"""Includes validation rules for supermodels."""
import re
from dataclasses import dataclass, field, fields
from typing import Any, Optional, Pattern

TNumeric = int | float

rule_field = lambda validator: field(default=None, metadata={"validator": validator})


@dataclass
class NewRules:
    """Provides validation rules for supermodels."""

    min: Optional[TNumeric] = rule_field(lambda x: lambda v: v >= x)
    max: Optional[TNumeric] = rule_field(lambda x: lambda v: v <= x)
    min_len: Optional[TNumeric] = rule_field(lambda x: lambda v: len(v) >= x)
    max_len: Optional[TNumeric] = rule_field(lambda x: lambda v: len(v) <= x)

    match: Optional[Pattern[str]] = rule_field(
        lambda x: lambda v: x.match(v) is not None
    )

    def validate(self, value: Any) -> list[tuple[str, Any]]:
        """Returns any rules that were violated by the provided value."""
        fails = []

        for own_field in fields(self):
            rule_name = own_field.name
            rule_value = getattr(self, rule_name)

            if not rule_value:
                continue

            validator = own_field.metadata["validator"]

            if not (validator(rule_value)(value)):
                if isinstance(rule_value, re.Pattern):
                    rule_value = f"'{rule_value.pattern}'"

                fails.append((rule_name, rule_value))

        return fails
