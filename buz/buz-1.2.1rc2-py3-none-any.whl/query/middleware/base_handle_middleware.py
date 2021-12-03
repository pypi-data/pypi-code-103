from abc import abstractmethod

from buz.query import Query, QueryHandler, QueryResponse
from buz.query.middleware import HandleMiddleware, HandleCallable


class BaseHandleMiddleware(HandleMiddleware):
    def on_handle(self, query: Query, query_handler: QueryHandler, handle: HandleCallable) -> QueryResponse:
        self._before_on_handle(query, query_handler)
        query_response = handle(query, query_handler)
        return self._after_on_handle(query, query_handler, query_response)

    @abstractmethod
    def _before_on_handle(self, query: Query, query_handler: QueryHandler) -> None:
        pass

    @abstractmethod
    def _after_on_handle(
        self, query: Query, query_handler: QueryHandler, query_response: QueryResponse
    ) -> QueryResponse:
        pass
