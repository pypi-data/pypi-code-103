from baby_steps import given, then, when
from district42 import schema
from jj.mock import HistoryRequest
from multidict import CIMultiDict, MultiDict
from revolt import substitute
from th import PathHolder
from valera import validate
from valera.errors import (
    ExtraKeyValidationError,
    SchemaMismatchValidationError,
    TypeValidationError,
    ValueValidationError,
)

from jj_district42 import HistoryRequestSchema

from ._utils import make_history_request


def test_request_history_type_validation():
    with given:
        sch = HistoryRequestSchema()
        req = make_history_request()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_type_validation_error():
    with given:
        sch = HistoryRequestSchema()
        value = []

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            TypeValidationError(PathHolder(), value, HistoryRequest)
        ]


def test_request_history_method_validation():
    with given:
        method = "GET"
        sch = substitute(HistoryRequestSchema(), {"method": method})
        req = make_history_request(method=method)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_method_validation_error():
    with given:
        expected_method, actual_method = "GET", "POST"
        sch = substitute(HistoryRequestSchema(), {"method": expected_method})
        req = make_history_request(method=actual_method)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["method"], actual_method, expected_method)
        ]


def test_request_history_path_validation():
    with given:
        path = "/users"
        sch = substitute(HistoryRequestSchema(), {"path": path})
        req = make_history_request(path=path)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_path_validation_error():
    with given:
        expected_path, actual_path = "/users", "/"
        sch = substitute(HistoryRequestSchema(), {"path": expected_path})
        req = make_history_request(path=actual_path)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["path"], actual_path, expected_path)
        ]


def test_request_history_segments_validation():
    with given:
        segments = {"user_id": "1"}
        sch = substitute(HistoryRequestSchema(), {"segments": segments})
        req = make_history_request(segments=segments)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_segments_validation_error():
    with given:
        expected_segments = {"user_id": "1"}
        actual_segments = {"user_id": "2"}
        sch = substitute(HistoryRequestSchema(), {"segments": expected_segments})
        req = make_history_request(segments=actual_segments)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["segments"]["user_id"],
                                 actual_segments["user_id"],
                                 expected_segments["user_id"])
        ]


def test_request_history_params_validation():
    with given:
        params = MultiDict({"user_id": "1"})
        sch = substitute(HistoryRequestSchema(), {"params": params})
        req = make_history_request(params=params)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_params_validation_error():
    with given:
        expected_params = MultiDict({"user_id": "1"})
        actual_params = MultiDict({"user_id": "2"})
        sch = substitute(HistoryRequestSchema(), {"params": expected_params})
        req = make_history_request(params=actual_params)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder()["params"]["user_id"],
                                 actual_params["user_id"],
                                 expected_params["user_id"])
        ]


def test_request_history_headers_validation():
    with given:
        headers = CIMultiDict({"user_id": "1"})
        sch = substitute(HistoryRequestSchema(), {"headers": headers})
        req = make_history_request(headers=headers)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_headers_validation_error():
    with given:
        expected_headers = CIMultiDict({"user_id": "1"})
        actual_headers = CIMultiDict({"user_id": "2"})
        sch = substitute(HistoryRequestSchema(), {"headers": expected_headers})
        req = make_history_request(headers=actual_headers)

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
        sch = substitute(HistoryRequestSchema(), {"body": body})
        req = make_history_request(body=body)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_body_validation_error():
    with given:
        expected_body, actual_body = "<expected>", "<actual>"
        sch = substitute(HistoryRequestSchema(), {"body": expected_body})
        req = make_history_request(body=actual_body)

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            SchemaMismatchValidationError(PathHolder()["body"],
                                          actual_body,
                                          (schema.str(expected_body),))
        ]


def test_request_history_validation():
    with given:
        req = {"method": "GET", "path": "/"}
        sch = HistoryRequestSchema()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == []


def test_request_history_validation_error():
    with given:
        req = {"method": "GET", "non_existing": "value"}
        sch = HistoryRequestSchema()

    with when:
        result = validate(sch, req)

    with then:
        assert result.get_errors() == [
            ExtraKeyValidationError(PathHolder(), req, "non_existing")
        ]
