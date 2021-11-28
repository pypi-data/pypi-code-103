from baby_steps import given, then, when
from district42 import schema
from district42_exp_types.ci_multi_dict import schema_ci_multi_dict
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from jj_district42 import HistoryResponseSchema

from ._utils import make_history_response


def test_history_response_substitution():
    with given:
        sch = HistoryResponseSchema()

    with when:
        res = substitute(sch, {})

    with then:
        assert id(res) != id(sch)


def test_history_response_status_substitution():
    with given:
        sch = HistoryResponseSchema()
        status = 200

    with when:
        res = substitute(sch, {
            "status": status
        })

    with then:
        assert res.props.status == schema.int(200).min(1)
        assert res != sch


def test_history_response_reason_substitution():
    with given:
        sch = HistoryResponseSchema()
        reason = "OK"

    with when:
        res = substitute(sch, {
            "reason": reason
        })

    with then:
        assert res.props.reason == schema.str(reason)
        assert res != sch


def test_history_response_headers_substitution():
    with given:
        sch = HistoryResponseSchema()
        headers = {"authorization": "banana"}

    with when:
        res = substitute(sch, {
            "headers": headers
        })

    with then:
        assert res.props.headers == schema_ci_multi_dict({
            "authorization": schema.str("banana")
        })
        assert res != sch


def test_history_response_body_substitution():
    with given:
        sch = HistoryResponseSchema()
        body = "<body>"

    with when:
        res = substitute(sch, {
            "body": body
        })

    with then:
        assert res.props.body == schema.any(schema.str(body))
        assert res != sch


def test_history_response_request_substitution_error():
    with given:
        sch = HistoryResponseSchema()
        res = make_history_response()

    with when, raises(Exception) as exception:
        sch % res

    with then:
        assert exception.type is SubstitutionError


def test_history_response_non_existing_key_substitution_error():
    with given:
        sch = HistoryResponseSchema()

    with when, raises(Exception) as exception:
        sch % {"non_existing": "value"}

    with then:
        assert exception.type is SubstitutionError


def test_history_response_invalid_value_substitution_error():
    with given:
        sch = HistoryResponseSchema()

    with when, raises(Exception) as exception:
        sch % {"status": "200"}

    with then:
        assert exception.type is SubstitutionError
