import pytest
import unittest.mock as mock

from ...funcs import assert_mutation

ADD_GIT_HUB_ADMIN_APP_TOKEN = """
mutation AddGitHubAdminAppToken($code: String!) {
  addGitHubAdminAppToken(code: $code) {
    ok
  }
}
"""

ALL_GITHUB_ADMIN_APP_TOKENS = """
{
  allGitHubTokens {
    totalCount
    edges {
      node {
        tokenId
        tokenMasked
        scope
      }
    }
  }
}
"""

HEADERS = {"Authorization": "Bearer token1"}  # user1


##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_store_token_for_code(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.schema.github.mutation.store_token_for_code", y)
    yield y


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": ADD_GIT_HUB_ADMIN_APP_TOKEN, "variables": {"code": "code_01234"}},
        {"query": ALL_GITHUB_ADMIN_APP_TOKENS},
        id="one",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_success(
    app,
    snapshot,
    data_mutation,
    data_query,
    mock_request_backup_db,
    mock_store_token_for_code,
):
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS,
        mock_request_backup_db,
        success=True,
    )
    snapshot.assert_match(mock_store_token_for_code.call_args_list)


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": ADD_GIT_HUB_ADMIN_APP_TOKEN, "variables": {"code": "code_01234"}},
        {"query": ALL_GITHUB_ADMIN_APP_TOKENS},
        id="one",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_error(
    app,
    snapshot,
    data_mutation,
    data_query,
    mock_request_backup_db,
    mock_store_token_for_code,
):
    mock_store_token_for_code.side_effect = Exception("error")
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS,
        mock_request_backup_db,
        success=False,
    )
    snapshot.assert_match(mock_store_token_for_code.call_args_list)


##__________________________________________________________________||
