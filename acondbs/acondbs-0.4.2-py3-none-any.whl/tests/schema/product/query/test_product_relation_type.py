import pytest

from ...funcs import assert_query

from ..gql import QUERY_PRODUCT_RELATION_TYPE

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION_TYPE,
            "variables": {"typeId": 1},
        },
        id="type_id",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION_TYPE,
            "variables": {"name": "parent"},
        },
        id="name",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION_TYPE,
            "variables": {"typeId": 1, "name": "parent"},
        },
        id="type_id-and-name",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_RELATION_TYPE,
            "variables": {"typeId": 2, "name": "parent"},
        },
        id="type_id-and-name-nonexistent)",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
