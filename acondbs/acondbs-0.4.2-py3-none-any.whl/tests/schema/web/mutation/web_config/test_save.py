import json

import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_SAVE_WEB_CONFIG, QUERY_WEB_CONFIG

HEADERS_MUTATION = {
    "Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"  # octocat
}

HEADERS_QUERY = {}

CONFIG_JSON = json.dumps(
    {
        "headTitle": "Saved Head Title",
        "toolbarTitle": "Saved Toolbar Title",
        "devtoolLoadingstate": False,
        "productCreationDialog": False,
        "productUpdateDialog": False,
        "productDeletionDialog": False,
    },
    indent=2,
)


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_SAVE_WEB_CONFIG,
            "variables": {
                "json": CONFIG_JSON,
            },
        },
        {"query": QUERY_WEB_CONFIG},
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
