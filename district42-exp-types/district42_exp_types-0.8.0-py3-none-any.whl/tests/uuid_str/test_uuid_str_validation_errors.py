from uuid import uuid4

from baby_steps import given, then, when
from th import PathHolder

from district42_exp_types.uuid_str import StrCaseValidationError


def test_validation_str_case_error():
    with given:
        value = str(uuid4())

    with when:
        res = StrCaseValidationError(PathHolder(), value, "lower")

    with then:
        assert repr(res) == f"StrCaseValidationError(PathHolder(), {value!r}, 'lower')"
