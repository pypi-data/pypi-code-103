import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_CREATE_PRODUCT_TYPE, QUERY_ALL_PRODUCT_TYPES

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [1, 2, 3],
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="create",
    ),
    pytest.param(
        {
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [2, 3, 3, 1, 2, 3, 1, 1],
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="field-ids-unsorted-duplicate",
    ),
    pytest.param(
        {
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="no-fields",
    ),
    pytest.param(
        {
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [],
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="empty-fields",
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
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "map",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "map",
                    "plural": "maps",
                    "icon": "mdi-map",
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="error-already-exist",
    ),
    pytest.param(
        {
            "query": MUTATION_CREATE_PRODUCT_TYPE,
            "variables": {
                "input": {
                    "name": "compass",
                    "order": 5,
                    "indefArticle": "a",
                    "singular": "compass",
                    "plural": "compasses",
                    "icon": "mdi-compass",
                    "fieldIds": [1, 2, 3, 88],
                }
            },
        },
        {"query": QUERY_ALL_PRODUCT_TYPES},
        id="non-existent-field",
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
