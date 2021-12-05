from baby_steps import given, then, when
from district42 import schema
from th import PathHolder

from district42_exp_types.unordered import UnorderedContainsValidationError


def test_validation_unordered_error():
    with given:
        sch = schema.str("banana")

    with when:
        res = UnorderedContainsValidationError(PathHolder(), sch)

    with then:
        assert repr(res) == f"UnorderedContainsValidationError(PathHolder(), {sch!r})"
