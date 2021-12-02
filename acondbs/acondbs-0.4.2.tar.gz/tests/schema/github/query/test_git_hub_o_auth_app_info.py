import pytest

from ...funcs import assert_query

GITHUB_OAUTH_APP_INFO = """
{
  gitHubOAuthAppInfo {
    clientId
    authorizeUrl
    redirectUri
  }
}
"""


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": GITHUB_OAUTH_APP_INFO},
        id="query",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data)


##__________________________________________________________________||
