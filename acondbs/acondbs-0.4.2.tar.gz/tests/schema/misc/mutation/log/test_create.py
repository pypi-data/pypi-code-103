import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_CREATE_LOG, QUERY_ALL_LOGS

HEADERS_MUTATION = {
}

HEADERS_QUERY = {
    "Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"  # octocat
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_CREATE_LOG,
            "variables": {
                "input": {
                    "level": "ERROR",
                    "message": "An exception is raised",
                }
            },
        },
        {"query": QUERY_ALL_LOGS},
        id="one",
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
        HEADERS_MUTATION,
        data_query,
        HEADERS_QUERY,
        mock_request_backup_db,
        success,
    )


##__________________________________________________________________||
