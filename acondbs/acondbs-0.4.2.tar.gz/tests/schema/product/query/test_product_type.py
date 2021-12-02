import pytest

from ...funcs import assert_query

from ..gql import QUERY_PRODUCT_TYPE

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


QUERY_PRODUCT_TYPE_SORT_PRODUCTS = """
{
  productType(typeId: 1) {
    typeId
    name
    order
    indefArticle
    singular
    plural
    icon
    products(sort: TIME_POSTED_DESC) {
      edges {
        node {
          name
        }
      }
    }
  }
}
"""


##__________________________________________________________________||
params = [
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_TYPE,
            "variables": {"typeId": 1},
        },
        id="type_id",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_TYPE,
            "variables": {"name": "map"},
        },
        id="name",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_TYPE,
            "variables": {"typeId": 1, "name": "map"},
        },
        id="type_id-and-name",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_TYPE,
            "variables": {"typeId": 2, "name": "map"},
        },
        id="type_id-and-name-nonexistent",
    ),
    pytest.param(
        {
            #
            "query": QUERY_PRODUCT_TYPE_SORT_PRODUCTS,
        },
        id="type_id-sort-products",
    ),
]


##__________________________________________________________________||
@pytest.mark.parametrize("data", params)
@pytest.mark.asyncio
async def test_schema(app, snapshot, data):
    await assert_query(app, snapshot, data, HEADERS)


##__________________________________________________________________||
