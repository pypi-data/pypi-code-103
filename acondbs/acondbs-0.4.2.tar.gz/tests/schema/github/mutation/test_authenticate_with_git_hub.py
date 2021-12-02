import textwrap
from async_asgi_testclient import TestClient

from a2wsgi import WSGIMiddleware

import pytest
import unittest.mock as mock


##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_authenticate(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.schema.github.mutation.authenticate", y)
    yield y


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_auth(app, mock_authenticate):

    query = textwrap.dedent(
        """
        mutation AuthenticateWithGitHub($code: String!) {
          authenticateWithGitHub(code: $code) {
            authPayload {
              token
            }
          }
        }
    """[
            1:
        ]
    )

    variables = {"code": "h443xg9c"}

    return_value = {"access_token": "jpdq74xt", "token_type": "bearer", "scope": ""}
    mock_authenticate.return_value = dict(return_value)

    expected = {"authenticateWithGitHub": {"authPayload": {"token": "jpdq74xt"}}}

    app = WSGIMiddleware(app)  # convert a wsgi app to an asgi app

    data = {"query": query, "variables": variables}

    headers = {"Content-Type:": "application/json"}

    async with TestClient(app) as client:
        resp = await client.post("/graphql", json=data, headers=headers)

    assert {"data": expected} == resp.json()
    assert [mock.call("h443xg9c")] == mock_authenticate.call_args_list


##__________________________________________________________________||
