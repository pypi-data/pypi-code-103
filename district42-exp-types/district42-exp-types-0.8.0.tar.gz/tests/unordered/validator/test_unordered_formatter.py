from baby_steps import given, then, when
from district42 import schema
from th import _

from district42_exp_types.unordered import UnorderedContainsValidationError, UnorderedFormatter


def test_format_unordered_error():
    with given:
        sch = schema.str("banana")
        error = UnorderedContainsValidationError(_, sch)
        formatter = UnorderedFormatter()

    with when:
        res = error.format(formatter)

    with then:
        assert res == f"Value must contain {sch!r}"


def test_format_nested_unordered_error():
    with given:
        sch = schema.str("banana")
        error = UnorderedContainsValidationError(_['id'], sch)
        formatter = UnorderedFormatter()

    with when:
        res = error.format(formatter)

    with then:
        assert res == f"Value at _['id'] must contain {sch!r}"
