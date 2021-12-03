from typing import Collection

from buz.query import Query, QueryHandler


class MoreThanOneQueryHandlerRelatedException(Exception):
    def __init__(self, query: Query, query_handlers: Collection[QueryHandler]):
        self.query = query
        self.query_handlers = query_handlers
        super().__init__(f"There is more than one handler registered for {query.fqn()}.")
