import pytest
from baby_steps import given, then, when
from district42 import represent

from district42_exp_types.numeric import schema_numeric


def test_numeric_representation():
    with given:
        sch = schema_numeric

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.numeric"


@pytest.mark.parametrize(
    ("value", "expected_repr"),
    [
        ("42", "schema.numeric('42')"),
        ("0", "schema.numeric('0')"),
        ("-42", "schema.numeric('-42')"),
    ]
)
def test_numeric_value_representation(value: str, expected_repr: str):
    with given:
        sch = schema_numeric(value)

    with when:
        res = represent(sch)

    with then:
        assert res == expected_repr


def test_numeric_min_value_representation():
    with given:
        sch = schema_numeric.min(42)

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.numeric.min(42)"


def test_numeric_max_value_representation():
    with given:
        sch = schema_numeric.max(42)

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.numeric.max(42)"


def test_numeric_min_max_value_representation():
    with given:
        sch = schema_numeric.min(1).max(2)

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.numeric.min(1).max(2)"


def test_numeric_min_max_with_value_representation():
    with given:
        sch = schema_numeric("2").min(1).max(3)

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.numeric('2').min(1).max(3)"
