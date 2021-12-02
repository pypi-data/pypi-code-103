import pytest

from ....funcs import assert_mutation

from ...gql import (
    MUTATION_UPDATE_PRODUCT_TYPE,
    QUERY_ALL_PRODUCT_TYPES,
)


HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT_TYPE,
            "variables": {
                "typeId": 1,
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [1, 4, 5],
                },
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="update",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT_TYPE,
            "variables": {
                "typeId": 1,
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [],
                },
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="empty-fields",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT_TYPE,
            "variables": {
                "typeId": 1,
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                },
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="fields-unchanged",
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
            "query": MUTATION_UPDATE_PRODUCT_TYPE,
            "variables": {
                "typeId": 5,
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                },
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="error-nonexistent",
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
