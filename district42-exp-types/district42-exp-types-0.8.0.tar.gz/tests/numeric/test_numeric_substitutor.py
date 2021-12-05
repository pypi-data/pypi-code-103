import pytest
from baby_steps import given, then, when
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.numeric import schema_numeric


def test_numeric_substitution():
    with given:
        sch = schema_numeric

    with when:
        res = substitute(sch, "42")

    with then:
        assert res == schema_numeric("42")
        assert res != sch


def test_numeric_value_substitution():
    with given:
        value = "42"
        sch = schema_numeric(value)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_numeric(value)
        assert id(res) != id(sch)


def test_numeric_substitution_invalid_value_error():
    with given:
        sch = schema_numeric("42")

    with when, raises(Exception) as exception:
        substitute(sch, 42)

    with then:
        assert exception.type is SubstitutionError


def test_numeric_substitution_incorrect_value_error():
    with given:
        sch = schema_numeric("42")

    with when, raises(Exception) as exception:
        substitute(sch, "50")

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", ["2", "1"])
def test_numeric_substitution_min(value: str):
    with given:
        sch = schema_numeric.min(1)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_numeric(value).min(1)
        assert res != sch


def test_numeric_substitution_min_value_error():
    with given:
        sch = schema_numeric.min(1)

    with when, raises(Exception) as exception:
        substitute(sch, "0")

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", ["0", "1"])
def test_numeric_substitution_max(value: str):
    with given:
        sch = schema_numeric.max(1)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_numeric(value).max(1)
        assert res != sch


def test_numeric_substitution_max_value_error():
    with given:
        sch = schema_numeric.max(1)

    with when, raises(Exception) as exception:
        substitute(sch, "2")

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", ["1", "2", "3"])
def test_numeric_substitution_min_max(value: str):
    with given:
        sch = schema_numeric.min(1).max(3)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_numeric(value).min(1).max(3)
        assert res != sch


@pytest.mark.parametrize("value", ["0", "4"])
def test_numeric_substitution_min_max_value_error(value: str):
    with given:
        sch = schema_numeric.min(1).max(3)

    with when, raises(Exception) as exception:
        substitute(sch, value)

    with then:
        assert exception.type is SubstitutionError
