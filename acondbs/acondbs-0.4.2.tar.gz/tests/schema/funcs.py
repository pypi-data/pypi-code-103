from async_asgi_testclient import TestClient
from a2wsgi import WSGIMiddleware


HEADERS_DEFAULT = {"Content-Type:": "application/json"}


##__________________________________________________________________||
async def assert_query(app, snapshot, data, headers=None, error=False):
    if not headers:
        headers = {}

    app = WSGIMiddleware(app)  # convert a wsgi app to an asgi app

    headers_custom = headers
    headers = HEADERS_DEFAULT.copy()
    headers.update(headers_custom)

    async with TestClient(app) as client:
        resp = await client.post("/graphql", json=data, headers=headers)

    resp_json = resp.json()

    # assert errors
    if error:
        assert "errors" in resp_json
        return

    assert "errors" not in resp_json

    # snapshot test
    #   https://github.com/syrusakbary/snapshottest/
    snapshot.assert_match(resp_json)


async def assert_mutation(
    app,
    snapshot,
    data_mutation,
    headers_mutation,
    data_query,
    headers_query,
    mock_request_backup_db,
    success=True,
):
    if success:
        mock_request_backup_db.reset_mock()

    await assert_query(
        app, snapshot, data_mutation, headers_mutation, error=not success
    )

    if success:
        mock_request_backup_db.assert_called_once()

    await assert_query(app, snapshot, data_query, headers_query)


##__________________________________________________________________||
