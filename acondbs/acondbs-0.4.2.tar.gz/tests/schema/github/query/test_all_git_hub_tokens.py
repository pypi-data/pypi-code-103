import pytest

from ...funcs import assert_query

GITHUB_TOKEN_FRAGMENT = """
fragment GitHubTokenFragment on GitHubToken {
  tokenId
  tokenMasked
  scope
  timeCreated
  user {
    login
  }
}
"""

ALL_GITHUB_TOKENS = (
    """
{
  allGitHubTokens {
    totalCount
    edges {
      node {
        ...GitHubTokenFragment
      }
    }
  }
}
"""
    + GITHUB_TOKEN_FRAGMENT
)

ALL_GITHUB_TOKENS_WITH_ORG_ACCESS = (
    """
{
  allGitHubTokens(filters: { scopeIlike: "%read:org%" }) {
    totalCount
    edges {
      node {
        ...GitHubTokenFragment
      }
    }
  }
}
"""
    + GITHUB_TOKEN_FRAGMENT
)

HEADERS = {
    "Authorization": "Bearer token1"  # user1
}


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": ALL_GITHUB_TOKENS},
        id="simple",
    ),
    pytest.param(
        {"query": ALL_GITHUB_TOKENS_WITH_ORG_ACCESS},
        id="filter",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)

##__________________________________________________________________||
