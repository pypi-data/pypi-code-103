import pytest
import unittest.mock as mock

from acondbs.github.ops import exchange_code_for_token

##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_call(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.github.ops.call", y)
    yield y

##__________________________________________________________________||
def test_call(app, snapshot, mock_call):
    code = "kp5b8653"
    return_value = {'access_token': "wuk5phc8", 'token_type': 'bearer', 'scope': 'user'}
    mock_call.exchange_code_for_token.return_value = dict(return_value)
    with app.app_context():
        ret = exchange_code_for_token(code)
    assert ret == return_value
    snapshot.assert_match(mock_call.exchange_code_for_token.call_args_list)

##__________________________________________________________________||
