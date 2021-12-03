from typing import List, Optional

from buz.locator import Locator
from buz.query import QueryBus, Query, QueryHandler, QueryResponse
from buz.query.middleware import HandleMiddleware, HandleMiddlewareChainResolver
from buz.query.sync import MoreThanOneQueryHandlerRelatedException


class SyncQueryBus(QueryBus):
    def __init__(
        self,
        locator: Locator[Query, QueryHandler],
        middlewares: Optional[List[HandleMiddleware]] = None,
    ):
        self.__locator = locator
        self.__handle_middleware_chain_resolver = HandleMiddlewareChainResolver(middlewares or [])

    def handle(self, query: Query) -> QueryResponse:
        query_handlers = self.__locator.get(query)

        if len(query_handlers) > 1:
            raise MoreThanOneQueryHandlerRelatedException(query, query_handlers)

        query_handler = query_handlers[0]
        return self.__handle_middleware_chain_resolver.resolve(query, query_handler, self.__perform_handle)

    def __perform_handle(self, query: Query, query_handler: QueryHandler) -> QueryResponse:
        return query_handler.handle(query)
