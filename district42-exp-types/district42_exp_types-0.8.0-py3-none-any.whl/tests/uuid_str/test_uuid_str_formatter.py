from uuid import uuid4

from baby_steps import given, then, when
from th import _

from district42_exp_types.uuid_str import StrCaseFormatter, StrCaseValidationError


def test_format_str_case_error():
    with given:
        value = str(uuid4())
        error = StrCaseValidationError(_, actual_value=value, expected_case="lower")
        formatter = StrCaseFormatter()

    with when:
        res = error.format(formatter)

    with then:
        assert res == f"Value <class 'str'> must be in lower case, but {value!r} given"


def test_format_nested_str_case_error():
    with given:
        value = str(uuid4())
        error = StrCaseValidationError(_['id'], actual_value=value, expected_case="upper")
        formatter = StrCaseFormatter()

    with when:
        res = error.format(formatter)

    with then:
        assert res == f"Value <class 'str'> at _['id'] must be in upper case, but {value!r} given"
