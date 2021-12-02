import pytest

from ...funcs import assert_query

from ..gql import (
    QUERY_ALL_PRODUCTS,
    QUERY_ALL_PRODUCTS_SHALLOW,
    QUERY_ALL_PRODUCTS_TOTAL_COUNT,
)

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS
        },
        id="deep",
    ),
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {"first": 2},
        },
        id="first-two",
    ),
    pytest.param(
        {
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {
                #
                "first": 2,
                "sort": "TIME_POSTED_DESC",
            },
        },
        id="first-two-sort",
    ),
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {
                #
                "filters": {"typeId": 1},
                "first": 2,
            },
        },
        id="filters-type_id-first-two",
    ),
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {
                #
                "filters": {"typeName": "map"},
                "first": 2,
            },
        },
        id="filters-type_name-first-two",
    ),
    pytest.param(
        {
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {
                #
                "filters": {"typeId": 1},
                "sort": "TIME_POSTED_DESC",
            },
        },
        id="filters-type_id-sort",
    ),
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS_SHALLOW,
            "variables": {
                #
                "filters": {"typeName": "map"},
                "sort": "TIME_POSTED_DESC",
            },
        },
        id="filters-type_name-sort",
    ),
    pytest.param(
        {
            #
            "query": QUERY_ALL_PRODUCTS_TOTAL_COUNT,
            "variables": {
                #
                "filters": {"typeName": "map"},
                "first": 2,
            },
        },
        id="total-count",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
