import orjson
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from requests import Request

from monite.server.errors import application_exception
from tests.server.simple_app.app.app import app

client = TestClient(app)
headers = {"x-request-id": "1111", "x-service-name": "fwefwe"}


def test_app_error():
    try:
        print(1 + "1")
    except TypeError as e:
        prepared_request = Request(
            method="GET",
            url="http://testserver/v1/appError",
        )
        r = application_exception(request=prepared_request, exc=e)
        assert orjson.loads(r.body) == {"error": {"message": "Server Error"}}


def test_prometheus():
    resp = client.get(
        "/metrics",
    )
    assert resp.status_code == 200


def test_root():
    resp = client.get(
        "/v1/",
        headers=headers,
    )
    assert resp.json() == {"Hello": "World"}


def test_ping():
    resp = client.get(
        "/readiness",
    )
    assert resp.status_code == 200
    assert resp.text == "pong"


def test_healthz():
    resp = client.get(
        "/liveness",
    )
    assert resp.status_code == 200
    assert resp.json() == {"temperature": 36.6}


def test_missing_endpoint():
    resp = client.get(
        "/missing_endpoint",
    )
    assert resp.status_code == 404


def test_http_error_validaton():
    resp = client.get("/v1/httpErrorValidation", headers=headers)
    assert resp.json() == "simple error"


def test_accept_language():
    # Default language
    headers.update({"Accept-Language": "en"})
    resp = client.get("/v1/", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["accept-language"] == "en"

    # German as an alternative language
    headers.update({"Accept-Language": "de"})
    resp = client.get("/v1/", headers=headers)

    assert resp.status_code == 200
    assert resp.headers["accept-language"] == "de"

    # Unexpected/unsupported language
    headers.update({"Accept-Language": "some-unexpected"})
    resp = client.get("/v1/", headers=headers)

    assert resp.status_code == 200
    assert resp.headers["accept-language"] == "en"


def test_x_accept_language():
    # Should return status code 415 if language not ISO-639-1
    headers.update(
        {"X-Accept-Language": "english"},
    )
    try:
        resp = client.get("/v1/", headers=headers)
    except HTTPException as resp:
        assert resp.status_code == 415
        assert resp.headers["X-Error"] == "Invalid API headers"

    # The language we are not support yet
    headers.update(
        {"X-Accept-Language": "ee"},
    )
    resp = client.get("/v1/", headers=headers)

    assert resp.status_code == 200
    assert resp.headers["accept-language"] == "en"
    assert resp.headers["x-accept-language"] == "en"

    # German as an alternative language
    headers.update(
        {
            "Accept-Language": "en",
            "X-Accept-Language": "de",
        },
    )
    resp = client.get("/v1/", headers=headers)

    assert resp.status_code == 200
    assert resp.headers["accept-language"] == "de"
    assert resp.headers["x-accept-language"] == "de"


if __name__ == "__main__":
    pass
