# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from aiohttp.web import StreamResponse

from contrast.extern import structlog as logging
from contrast.agent.middlewares.base_middleware import BaseMiddleware

logger = logging.getLogger("contrast")


class AioHttpMiddleware(BaseMiddleware):
    __middleware_version__ = 1  # Aiohttp new-style middleware

    def __init__(self, app_name=None):
        self.app = None
        self.app_name = app_name
        super(AioHttpMiddleware, self).__init__()

    async def __call__(self, request, handler) -> StreamResponse:
        self.app = request.app
        logger.debug("nothing happening yet")
        return await self.call_without_agent_async(request, handler)

    async def call_without_agent_async(self, request, handler) -> StreamResponse:
        super(AioHttpMiddleware, self).call_without_agent()
        return await handler(request)
