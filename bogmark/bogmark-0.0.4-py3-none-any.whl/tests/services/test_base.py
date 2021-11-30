import os
from pathlib import Path
from unittest import mock

import pytest

from monite.services import BaseAsyncRequester

environ = {"SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_init(result_holder):
    with mock.patch.dict(os.environ, environ):
        Path("settings").mkdir(exist_ok=True)
        f = open("settings/.env", "w")
        f.close()
        ba = BaseAsyncRequester()
        ba_auth = BaseAsyncRequester(login="ci", password="ci")
        result_holder["ba_obj"] = ba
        result_holder["ba_auth_obj"] = ba_auth


@pytest.mark.asyncio
async def test_serializer(result_holder):
    ba: BaseAsyncRequester = result_holder["ba_obj"]
    assert '{"fefew":1}' == ba.serialize({"fefew": 1})


@pytest.mark.asyncio
async def test_get_url(result_holder):
    ba: BaseAsyncRequester = result_holder["ba_obj"]
    assert ba.get_base_url() == "http://localhost"


@pytest.mark.asyncio
async def test_get_headers(result_holder):
    ba: BaseAsyncRequester = result_holder["ba_obj"]
    assert ba._get_headers() == {"X-REQUEST-ID": "default_request_id", "X-SERVICE-NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_request(result_holder):
    ba: BaseAsyncRequester = result_holder["ba_obj"]
    ba_auth: BaseAsyncRequester = result_holder["ba_auth_obj"]
    await ba._make_json_request(method="GET", url="http://ya.ru")
    await ba_auth._make_json_request(method="GET", url="http://ya.ru")
    await ba._make_json_request(method="GET", url="http://ya.ru", timeout=0.01)


if __name__ == "__main__":
    pass
