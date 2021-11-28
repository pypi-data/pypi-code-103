from baby_steps import given, then, when
from district42 import schema
from jj.mock import HistoryResponse
from multidict import CIMultiDict
from revolt import substitute
from th import PathHolder
from valera import validate
from valera.errors import (
    ExtraKeyValidationError,
    SchemaMismatchValidationError,
    TypeValidationError,
    ValueValidationError,
)

from jj_district42 import HistoryResponseSchema

from ._utils import make_history_response


def test_response_history_type_validation():
    with given:
        sch = HistoryResponseSchema()
        req = make_history_response()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_resposne_history_type_validation_error():
    with given:
        sch = HistoryResponseSchema()
        value = []

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            TypeValidationError(PathHolder(), value, HistoryResponse)
        ]


def test_response_history_status_validation():
    with given:
        status = 200
        sch = substitute(HistoryResponseSchema(), {"status": status})
        req = make_history_response(status=status)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_response_history_status_validation_error():
    with given:
        expected_status, actual_status = 200, 404
        sch = substitute(HistoryResponseSchema(), {"status": expected_status})
        req = make_history_response(status=actual_status)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["status"], actual_status, expected_status)
        ]


def test_response_history_reason_validation():
    with given:
        reason = "OK"
        sch = substitute(HistoryResponseSchema(), {"reason": reason})
        req = make_history_response(reason=reason)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_response_history_reason_validation_error():
    with given:
        expected_reason, actual_reason = "OK", "Not Found"
        sch = substitute(HistoryResponseSchema(), {"reason": expected_reason})
        req = make_history_response(reason=actual_reason)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["reason"], actual_reason, expected_reason)
        ]


def test_response_history_headers_validation():
    with given:
        headers = CIMultiDict({"user_id": "1"})
        sch = substitute(HistoryResponseSchema(), {"headers": headers})
        req = make_history_response(headers=headers)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_response_history_headers_validation_error():
    with given:
        expected_headers = CIMultiDict({"user_id": "1"})
        actual_headers = CIMultiDict({"user_id": "2"})
        sch = substitute(HistoryResponseSchema(), {"headers": expected_headers})
        req = make_history_response(headers=actual_headers)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["headers"]["user_id"],
                                 actual_headers["user_id"],
                                 expected_headers["user_id"])
        ]


def test_request_history_body_validation():
    with given:
        body = ""
        sch = substitute(HistoryResponseSchema(), {"body": body})
        req = make_history_response(body=body)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_body_validation_error():
    with given:
        expected_body, actual_body = "<expected>", "<actual>"
        sch = substitute(HistoryResponseSchema(), {"body": expected_body})
        req = make_history_response(body=actual_body)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            SchemaMismatchValidationError(PathHolder()["body"],
                                          actual_body,
                                          (schema.str(expected_body),))
        ]


def test_response_history_validation():
    with given:
        req = {"status": 200, "reason": "OK"}
        sch = HistoryResponseSchema()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_response_history_validation_error():
    with given:
        req = {"status": 200, "non_existing": "value"}
        sch = HistoryResponseSchema()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ExtraKeyValidationError(PathHolder(), req, "non_existing")
        ]
