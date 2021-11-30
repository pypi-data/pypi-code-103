from aiohttp.client import ClientResponse

from monite.structures.response import MoniteJSONResponse


async def simple_200_resp(*args, **kwargs):
    return MoniteJSONResponse(status_code=200, content={"sss": 1})


async def simple_500_resp(*args, **kwargs):
    return MoniteJSONResponse(status_code=500, content="Oops")


async def aiohttp_mock_resp(*args, **kwargs):
    return ClientResponse()


async def simple_json_200_resp(*args, **kwargs):
    return MoniteJSONResponse(status_code=200, content={"Hello": "World"})
