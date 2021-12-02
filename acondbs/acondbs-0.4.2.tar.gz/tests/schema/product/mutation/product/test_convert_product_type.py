import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_CONVERT_PRODUCT_TYPE, QUERY_ALL_PRODUCTS

HEADERS = {
    "Authorization": "Bearer 39d86487d76a84087f1da599c872dac4473e5f07",  # user1
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_CONVERT_PRODUCT_TYPE,
            "variables": {
                "productId": 1,
                "typeId": 2,
            },
        },
        {"query": QUERY_ALL_PRODUCTS},
        id="convert",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_success(
    app, snapshot, data_mutation, data_query, mock_request_backup_db
):
    success = True
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS,
        mock_request_backup_db,
        success,
    )


##__________________________________________________________________||
