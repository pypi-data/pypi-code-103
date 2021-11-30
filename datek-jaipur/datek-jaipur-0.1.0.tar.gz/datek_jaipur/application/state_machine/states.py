from abc import ABC, ABCMeta
from functools import wraps
from typing import Optional, Type

from datek_async_fsm.state import BaseState as _BaseState, StateCollection, StateType

from datek_jaipur.application.state_machine.scope import Scope
from datek_jaipur.errors import JaipurError


def catch_jaipur_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except JaipurError:
            pass

    return wrapper


class BaseStateMeta(ABCMeta):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        class_ = super().__new__(mcs, name, bases, namespace)
        class_.transit = catch_jaipur_error(class_.transit)
        return class_


class BaseState(_BaseState, ABC, metaclass=BaseStateMeta):
    pass


class Start(BaseState):
    scope: Scope

    @staticmethod
    def type() -> StateType:
        return StateType.INITIAL

    async def transit(self, states: StateCollection) -> Optional[Type["BaseState"]]:
        adapter = self.scope.adapter_class(self.__class__)
        self.scope.game = await adapter.collect_data()
        return PlayerTurn


class PlayerTurn(BaseState):
    scope: Scope

    @staticmethod
    def type() -> StateType:
        return StateType.STANDARD

    async def transit(self, states: StateCollection) -> Optional[Type["BaseState"]]:
        adapter = self.scope.adapter_class(
            state_class=self.__class__,
            game=self.scope.game,
        )

        self.scope.game = await adapter.collect_data()

        return PlayerWon if self.scope.game.winner else PlayerTurn


class PlayerWon(BaseState):
    scope: Scope

    @staticmethod
    def type() -> StateType:
        return StateType.STANDARD

    async def transit(self, states: StateCollection) -> Optional[Type["BaseState"]]:
        adapter = self.scope.adapter_class(
            state_class=self.__class__,
            game=self.scope.game,
        )

        return await adapter.collect_data()


class End(BaseState):
    @staticmethod
    def type() -> StateType:
        return StateType.END

    async def transit(
        self, states: StateCollection
    ) -> Optional[Type["BaseState"]]:  # pragma no cover
        pass
