import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_CREATE_FIELD, QUERY_ALL_FIELDS

HEADERS = {
    "Authorization": "Bearer 0fb8c9e16d6f7c4961c4c49212bf197d79f14080"  # dojocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_CREATE_FIELD,
            "variables": {
                "input": {
                    "name": "author",
                    "type_": "UNICODE_TEXT",
                }
            },
        },
        {"query": QUERY_ALL_FIELDS},
        id="by-enum-name",
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
            "query": MUTATION_CREATE_FIELD,
            "variables": {
                "input": {
                    "name": "author",
                    "type_": 1,
                }
            },
        },
        {"query": QUERY_ALL_FIELDS},
        id="by-enum-int",
    ),
    pytest.param(
        {
            "query": MUTATION_CREATE_FIELD,
            "variables": {
                "input": {
                    "name": "author",
                    "type_": "NONEXISTENT_ENUM",
                }
            },
        },
        {"query": QUERY_ALL_FIELDS},
        id="enum-nonexistent",
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
