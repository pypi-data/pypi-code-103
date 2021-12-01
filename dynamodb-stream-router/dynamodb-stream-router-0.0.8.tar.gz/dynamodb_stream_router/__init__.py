from __future__ import annotations

from concurrent.futures import Executor
from enum import Enum, auto
from functools import partial
from itertools import groupby
from types import FunctionType
from typing import Any, Callable

from multipledispatch import dispatch

from .conditions import Condition
from .conditions.parser import ExpressionParser
from .exceptions import RouteAlreadyExistsException
from .record import Record, RouteRecord


class Operation(Enum):
    INSERT = auto()
    MODIFY = auto()
    REMOVE = auto()


DYNAMODB_STREAM_ROUTER_NAMESPACE = dict()
dispatch = partial(dispatch, namespace=DYNAMODB_STREAM_ROUTER_NAMESPACE)

__CONDITION_PARSER = ExpressionParser()
__ROUTES: dict[Operation, set[Route]] = {operation: set() for operation in Operation}

RouteHandler = Callable[[RouteRecord], Any]


class Route:
    def __call__(self, record: RouteRecord) -> Any:
        return self.__handler(record)

    def __hash__(self) -> int:
        return hash(self.__condition)

    def __init__(
        self, *, condition: Condition, handler: RouteHandler, priority: int
    ) -> None:
        super().__init__()
        self.__condition = condition
        self.__priority = priority
        self.__handler = handler

    def __str__(self) -> str:
        return f"{self.__condition}[{self.__priority}] -> {self.__handler.__module__}.{self.__handler.__name__}"

    @property
    def _condition(self) -> Condition:
        return self.__condition

    @property
    def _handler(self) -> RouteHandler:
        return self.__handler

    @property
    def _priority(self) -> int:
        return self.__priority

    def match(self, record: RouteRecord) -> bool:
        return self.__condition(record)


def add_route(operation: Operation, route: Route) -> Route:
    if route:
        if has_route(operation, route):
            raise RouteAlreadyExistsException()
        __ROUTES[operation].add(route)
    return route


def get_routes(operation: Operation) -> frozenset[Route]:
    return frozenset(__ROUTES[operation])


def has_route(operation: Operation, route: Route) -> bool:
    return route in __ROUTES[operation]


def remove_route(operation: Operation, route: Route) -> Route:
    try:
        __ROUTES[operation].remove(route)
    except KeyError:
        pass
    return route


def update_route(operation: Operation, route: Route) -> Route:
    if route:
        __ROUTES[operation].add(route)
    return route


RouteHandlerDecorator = Callable[[RouteHandler], Route]


@dispatch(int)
def on_insert(priority: int, /) -> RouteHandlerDecorator:
    return on_insert(lambda _: True, priority)


@dispatch(str, int)
def on_insert(condition: str, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.INSERT}, condition, priority)


@dispatch(FunctionType, int)
def on_insert(condition: Condition, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.INSERT}, condition, priority)


@dispatch(int)
def on_modify(priority: int, /) -> RouteHandlerDecorator:
    return on_modify(lambda _: True, priority)


@dispatch(str, int)
def on_modify(condition: str, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.MODIFY}, condition, priority)


@dispatch(FunctionType, int)
def on_modify(condition: Condition, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.MODIFY}, condition, priority)


@dispatch(int)
def on_remove(priority: int, /) -> RouteHandlerDecorator:
    return on_remove(lambda _: True, priority)


@dispatch(str, int)
def on_remove(condition: str, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.REMOVE}, condition, priority)


@dispatch(FunctionType, int)
def on_remove(condition: Condition, priority: int, /) -> RouteHandlerDecorator:
    return on_operations({Operation.REMOVE}, condition, priority)


@dispatch(set, int)
def on_operations(
    operations: set[Operation], priority: int, /
) -> RouteHandlerDecorator:
    return on_operations(operations, lambda _: True, priority)


@dispatch(set, str, int)
def on_operations(
    operations: set[Operation], condition: str, priority: int, /
) -> RouteHandlerDecorator:
    return on_operations(operations, __CONDITION_PARSER.parse(condition), priority)


@dispatch(set, FunctionType, int)
def on_operations(
    operations: set[Operation], condition: Condition, priority: int, /
) -> RouteHandlerDecorator:
    def register_route(handler: RouteHandler) -> RouteHandler:
        route = Route(condition=condition, handler=handler, priority=priority or 0)
        for operation in operations:
            add_route(operation, route)
        return handler

    return register_route


def route_record(
    record: Record,
    executor: Executor = None,
) -> None:
    operation = Operation[record["eventName"]]
    record: RouteRecord = RouteRecord(record)
    for _, routes in groupby(
        sorted(
            [route for route in __ROUTES[operation] if route.match(record)],
            key=lambda x: x._priority,
        ),
        key=lambda x: x._priority,
    ):
        routes = list(routes)
        routes[0](record) if len(routes) == 1 else list(
            (executor.map if executor else map)(
                Route.__call__, routes, [record] * len(routes)
            )
        )


def route_records(
    records: list[Record],
    executor: Executor = None,
) -> None:
    list(map(route_record, records, [executor] * len(records)))
