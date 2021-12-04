from app.api.api_client import ApiClient
from unittest.mock import Mock, patch, call
from pytest import raises
from app.utils.exceptions import EnvVarMissing


@patch("app.api.api_client.get_logger")
def test_logger_defaulted(mock_get_logger):
    client = ApiClient()
    logger = client._logger
    mock_get_logger.assert_called_once()


@patch("app.api.api_client.getenv")
def test_api_client(mock_getenv):
    client = ApiClient()
    key = client.api_key
    mock_getenv.assert_has_calls([call("DECY_GATEWAY_TOKEN"), call().__bool__(), call().__eq__("")])


@patch("app.api.api_client.sys.exit")
@patch("app.api.api_client.get_logger")
@patch("app.api.api_client.getenv")
def test_api_client_no_key(mock_getenv, mock_logger, mock_exit):
    mock_getenv.return_value = ""
    client = ApiClient()
    key = client.api_key
    mock_exit.assert_has_calls([call(1)])


@patch("app.api.api_client.ApiClient.api_key")
@patch("app.api.api_client.deepcopy")
@patch("app.api.api_client.RLock")
@patch("app.api.api_client.Session")
def test_session(mock_session, mock_rlock, mock_deepcopy, mock_key):
    client = ApiClient()
    session = client._session
    mock_session.assert_has_calls([call(), call().headers.update(mock_deepcopy())])
    mock_rlock.assert_has_calls([call(), call().__enter__(), call().__exit__(None, None, None)])
    mock_deepcopy.assert_has_calls(
        [call({"Content-Type": "application/json"}), call().__setitem__("header_auth", mock_key), call()]
    )


@patch("app.api.api_client.ApiClient._session")
@patch("app.api.api_client.ApiClient._build_uri")
def test_make_api_call_base_no_payload(mock_build_uri, mock_session):
    client = ApiClient()
    client._make_api_call_base("get", "asdf")
    mock_build_uri.assert_has_calls([call("asdf")])
    mock_session.assert_has_calls([call.get(mock_build_uri(), timeout=15)])


@patch("app.api.api_client.ApiClient._session")
@patch("app.api.api_client.ApiClient._build_uri")
def test_make_api_call_base_with_payload(mock_build_uri, mock_session):
    client = ApiClient()
    client._make_api_call_base("get", "asdf", {"asdf": "asdf"})
    mock_build_uri.assert_has_calls([call("asdf")])
    mock_session.assert_has_calls([call.get(mock_build_uri(), data={"asdf": "asdf"}, timeout=15)])


@patch("app.api.api_client.get_logger")
@patch("app.api.api_client.ApiClient._make_api_call_base")
def test_make_api_call_ok(mock_base_api, mock_logger):
    class MockObj:
        ok = True

        @staticmethod
        def json():
            return {"asdf": "asdf"}

    mock_base_api.return_value = MockObj
    client = ApiClient()
    response = client.make_api_call("get", "asdf")
    mock_base_api.assert_has_calls([call("get", "asdf", None)])
    assert response == {"asdf": "asdf"}


@patch("app.api.api_client.get_logger")
@patch("app.api.api_client.ApiClient._make_api_call_base")
def test_make_api_call_bad_json(mock_base_api, mock_logger):
    class MockObj:
        ok = True
        text = "test_response"

        @staticmethod
        def json():
            return int("asdf")

    mock_base_api.return_value = MockObj
    client = ApiClient()
    response = client.make_api_call("get", "asdf")
    assert response == "test_response"


@patch("app.api.api_client.sys.exit")
@patch("app.api.api_client.ApiClient._make_api_call_base")
def test_make_api_call_500(mock_base_api, mock_exit):
    class MockObj:
        ok = False
        status_code = 501
        message = "500 error"
        text = "asdf"
        headers = {"Message":"asdf"}
    mock_base_api.return_value = MockObj
    client = ApiClient()
    response = client.make_api_call("get", "asdf")
    mock_exit.assert_called()


@patch("app.api.api_client.sys.exit")
@patch("app.api.api_client.ApiClient._make_api_call_base")
def test_make_api_call_non_500(mock_base_api, mock_exit):
    class MockObj:
        ok = False
        status_code = 605
        message = "unknown error"
        text = "asdf"
        headers = "asdf"
    mock_base_api.return_value = MockObj
    client = ApiClient()
    response = client.make_api_call("get", "asdf")
    mock_exit.assert_called()


def test_build_uri_with_basepath():
    client = ApiClient()
    uri = client._build_uri("asdf")
    assert uri == f"{client._API_BASE_PATH}asdf"


def test_build_uri_without_basepath():
    client = ApiClient()
    uri = client._build_uri(f"{client._API_BASE_PATH}asdf")
    assert uri == f"{client._API_BASE_PATH}asdf"
