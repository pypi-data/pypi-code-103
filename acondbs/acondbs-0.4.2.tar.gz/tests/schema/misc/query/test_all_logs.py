import pytest

from ...funcs import assert_query

from ..gql import (
    QUERY_ALL_LOGS,
)

HEADERS = {
    "Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"  # octocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_ALL_LOGS
        },
        id="one",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
