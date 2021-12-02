import pytest

from ...funcs import assert_query

ALL_GITHUB_ORGS = '''
{
  allGitHubOrgs {
    totalCount
    edges {
      node {
        login
        memberships {
          totalCount
          edges {
            node {
              member {
                login
              }
            }
          }
        }
      }
    }
  }
}
'''

HEADERS = {
    "Authorization": "Bearer token1"  # user1
}


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": ALL_GITHUB_ORGS},
        id="one",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)

##__________________________________________________________________||
