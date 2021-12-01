from asyncio import ensure_future, get_event_loop
from logging import getLogger
from typing import Callable, Optional

from aiohttp.web import (
    Application,
    AppRunner,
    HTTPBadRequest,
    Request,
    Response,
    TCPSite,
    get,
    middleware,
    post,
    route,
)
from yarl import URL

from ._request import ProxyRequest

AGENT_NAME = "tecoroute-proxy/1.0 (+https://github.com/czetech/tecoroute-proxy)"

logger = getLogger(__name__)


class Proxy:
    """TODO."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 80,
        control: str = "/tecoroute-proxy",
        origin: str = "https://route.tecomat.com",
    ) -> None:
        """TODO."""
        self._host = host
        self._port = port
        self._baseurl = URL(origin)

        server = Application(middlewares=[self._middleware])
        control_path = URL("/").join(URL(control)).path
        server.add_routes(
            [
                get(control_path, self._handler_api_get),
                post(control_path, self._handler_api_post),
                route("*", "/{url:.*}", self._handler_all),
            ]
        )
        self._runner = AppRunner(server)

    @middleware
    async def _middleware(self, request: Request, handler: Callable[..., Response]):
        response = await handler(request)
        response.headers["Server"] = AGENT_NAME
        return response

    async def _handler_all(self, request):
        async with ProxyRequest(request) as proxy_request:
            return await proxy_request.response()

    async def _handler_api_get(self, request):
        return Response(text="OK")

    async def _handler_api_post(self, request):
        post = await request.post()
        action = post.get("action")
        if action == "login":
            login = {key: post.get(key, "") for key in ("user", "password", "plc")}
            login["username"] = login.pop("user")
            logger.info(f"New login as {login}")
            async with ProxyRequest(request) as proxy_request:
                return await proxy_request.login(**login)
        if action == "logout":
            return  # TODO: what return?
        else:
            raise (HTTPBadRequest())

    async def start(self) -> None:
        """Start TecoRoute Proxy server in event loop."""
        await self._runner.setup()
        await TCPSite(self._runner, self._host, self._port).start()
        logger.info(f"Tecoroute Proxy started on {self._host}:{self._port}")

    def run(self) -> None:
        """Run TecoRoute Proxy server."""
        ensure_future(self.start())
        get_event_loop().run_forever()
