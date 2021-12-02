import pytest

from ...funcs import assert_query

from ..gql import QUERY_FIELD

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_FIELD,
            "variables": {"fieldId": 1},
        },
        id="by-field-id",
    ),
    pytest.param(
        {
            #
            "query": QUERY_FIELD,
            "variables": {"name": "contact"},
        },
        id="by-name",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
