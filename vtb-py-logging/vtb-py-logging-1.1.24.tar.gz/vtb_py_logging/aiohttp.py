from aiohttp import web
from vtb_py_logging.request_id import RequestId
from vtb_py_logging.log_extra import push_extra


def request_id_middleware(prefix):
    @web.middleware
    async def inner(request, handler):
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            request_id = RequestId.make(prefix=prefix)
        push_extra(request_id=request_id)
        response = await handler(request)
        return response
    return inner
