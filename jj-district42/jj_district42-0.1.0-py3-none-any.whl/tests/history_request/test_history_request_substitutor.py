from baby_steps import given, then, when
from district42 import schema
from district42_exp_types.ci_multi_dict import schema_ci_multi_dict
from district42_exp_types.multi_dict import schema_multi_dict
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from jj_district42 import HistoryRequestSchema

from ._utils import make_history_request


def test_history_request_substitution():
    with given:
        sch = HistoryRequestSchema()

    with when:
        res = substitute(sch, {})

    with then:
        assert id(res) != id(sch)


def test_history_request_method_substitution():
    with given:
        sch = HistoryRequestSchema()
        method = "GET"

    with when:
        res = substitute(sch, {
            "method": method
        })

    with then:
        assert res.props.method == schema.str(method).len(1, ...)
        assert res != sch


def test_history_request_path_substitution():
    with given:
        sch = HistoryRequestSchema()
        path = "/users"

    with when:
        res = substitute(sch, {
            "path": path
        })

    with then:
        assert res.props.path == schema.str(path)
        assert res != sch


def test_history_request_segments_substitution():
    with given:
        sch = HistoryRequestSchema()
        segments = {"user_id": "1"}

    with when:
        res = substitute(sch, {
            "segments": segments
        })

    with then:
        assert res.props.segments == schema.dict({
            "user_id": schema.str("1")
        })
        assert res != sch


def test_history_request_params_substitution():
    with given:
        sch = HistoryRequestSchema()
        params = {"id": "1"}

    with when:
        res = substitute(sch, {
            "params": params
        })

    with then:
        assert res.props.params == schema_multi_dict({
            "id": schema.str("1")
        })
        assert res != sch


def test_history_request_headers_substitution():
    with given:
        sch = HistoryRequestSchema()
        headers = {"authorization": "banana"}

    with when:
        res = substitute(sch, {
            "headers": headers,
        })

    with then:
        assert res.props.headers == schema_ci_multi_dict({
            "authorization": schema.str("banana")
        })
        assert res != sch


def test_history_request_body_substitution():
    with given:
        sch = HistoryRequestSchema()
        body = "<body>"

    with when:
        res = substitute(sch, {
            "body": body
        })

    with then:
        assert res.props.body == schema.any(schema.str(body))
        assert res != sch


def test_history_request_request_substitution_error():
    with given:
        sch = HistoryRequestSchema()
        req = make_history_request()

    with when, raises(Exception) as exception:
        sch % req

    with then:
        assert exception.type is SubstitutionError


def test_history_request_non_existing_key_substitution_error():
    with given:
        sch = HistoryRequestSchema()

    with when, raises(Exception) as exception:
        sch % {"non_existing": "value"}

    with then:
        assert exception.type is SubstitutionError


def test_history_request_invalid_value_substitution_error():
    with given:
        sch = HistoryRequestSchema()

    with when, raises(Exception) as exception:
        sch % {"method": 1}

    with then:
        assert exception.type is SubstitutionError
