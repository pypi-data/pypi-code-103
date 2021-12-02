import pytest

from .funcs import assert_mutation

from .misc.gql import QUERY_ALL_LOGS

##__________________________________________________________________||
QUERY = """
{
  noSuchField
}
""".strip()

HEADERS = {
    "Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"  # octocat
}

HEADERS_QUERY = {
    "Authorization": "Bearer 90b2ee5fed25506df04fd37343bb68d1803dd97f"  # octocat
}


##__________________________________________________________________||
@pytest.fixture
def app(app_users):
    y = app_users
    yield y


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": QUERY,
            "variables": {"var1": 100},
        },
        {"query": QUERY_ALL_LOGS},
        id="one",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema(
    app, snapshot, data_mutation, data_query, mock_request_backup_db
):

    success = False
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS_QUERY,
        mock_request_backup_db,
        success,
    )


##__________________________________________________________________||
