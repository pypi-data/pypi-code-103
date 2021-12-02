import pytest

from ....funcs import assert_mutation

from ...gql import (
    FRAGMENT_PRODUCT_RELATION_TYPE_CONNECTION,
    MUTATION_UPDATE_PRODUCT_RELATION_TYPE,
)

##__________________________________________________________________||
QEURY = (
    """
{
  allProductRelationTypes {
   ...fragmentProductRelationTypeConnection
  }
}
"""
    + FRAGMENT_PRODUCT_RELATION_TYPE_CONNECTION
)

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT_RELATION_TYPE,
            "variables": {
                "typeId": 1,
                "input": {
                    "indefArticle": "an",
                    "singular": "mmap",
                    "plural": "mmaps",
                },
            },
        },
        {"query": QEURY},
        id="update",
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
params = [
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT_RELATION_TYPE,
            "variables": {
                "typeId": 1,
                "input": {
                    "name": "mmap",
                },
            },
        },
        {"query": QEURY},
        id="error-immutable-field",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_error(
    app, snapshot, data_mutation, data_query, mock_request_backup_db
):
    success = False
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
