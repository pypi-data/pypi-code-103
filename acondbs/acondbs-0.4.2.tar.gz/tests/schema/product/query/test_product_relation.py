import pytest

from ...funcs import assert_query

from ..gql import QUERY_PRODUCT_RELATION

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION,
            "variables": {"relationId": 1},
        },
        id="type_id",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION,
            "variables": {"relationId": 222},
        },
        id="type_id-nonexistent",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
