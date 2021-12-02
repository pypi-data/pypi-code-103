import pytest

from .funcs import assert_query

QUERY = '''
{
  __schema {
    types {
      kind
      name
      fields {
        name
      }
    }
    queryType {
      fields {
        name
      }
    }
    mutationType {
      fields {
        name
      }
    }
    subscriptionType {
      fields {
        name
      }
    }
  }
}
'''


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": QUERY},
        {"Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"},
        id="admin",
    ),
    pytest.param(
        {"query": QUERY},
        {"Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"},
        id="private",
    ),
    pytest.param(
        {"query": QUERY},
        {"Authorization": "Bearer 1a2d18f270df3abacfb85c5413b668f97794b4ce"},
        id="public-wrong-token",
    ),
    pytest.param(
        {"query": QUERY},
        {},
        id="public-no-token",
    ),
]


@pytest.mark.parametrize("data, headers", params)
@pytest.mark.asyncio
async def test_schema(app_users, snapshot, data, headers):
    await assert_query(app_users, snapshot, data, headers)


##__________________________________________________________________||
