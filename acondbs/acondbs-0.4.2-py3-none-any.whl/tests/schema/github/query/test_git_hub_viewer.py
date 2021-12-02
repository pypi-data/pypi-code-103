import pytest

from ...funcs import assert_query

QUERY = "{ gitHubViewer { login name avatarUrl } }"

##__________________________________________________________________||
params = [
    pytest.param(
        {"query": QUERY},
        {"Authorization": "Bearer token1"},
        id="one",
    ),
]


@pytest.mark.parametrize("data, headers", params)
@pytest.mark.asyncio
async def test_success(app, snapshot, data, headers):
    await assert_query(app, snapshot, data, headers)


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": QUERY},
        {"Authorization": "Bearer no-such-token"},
        id="wrong-token",
    ),
    pytest.param(
        {"query": QUERY},
        {},
        id="no-token",
    ),
]


@pytest.mark.parametrize("data, headers", params)
@pytest.mark.asyncio
async def test_error(app, snapshot, data, headers):
    await assert_query(app, snapshot, data, headers, error=True)


##__________________________________________________________________||
