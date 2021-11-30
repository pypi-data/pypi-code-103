import pytest
from fastapi.testclient import TestClient

from monite.server.assebmly import compile_routers
from monite.server.errors import BizLogicError
from monite.server.mixin import orjson_dumps
from tests.server.simple_app.app.app import app

client = TestClient(app)
headers = {"x-request-id": "1111", "x-service-name": "fwefwe"}


def test_biz_logic_error():
    BizLogicError(detail="THIS IS BIZ ERROR, bitch")


def test_orjson_dump():
    orjson_dumps({"fewfewf": 1}, default=None)


if __name__ == "__main__":
    pass
