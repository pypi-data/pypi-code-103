# -*- coding: utf-8 -*-
from pydantic.typing import get_class
from typing import TypeVar, Generic, Type, ClassVar

from pydantic import BaseModel
try:
    from starsessions import SessionBackend, SessionNotLoaded
except ImportError as exc:
    raise RuntimeError("can't use sessions without starsessions installed") from exc


DataType = TypeVar('DataType', bound=BaseModel)


class Session(Generic[DataType]):

    _data: DataType
    _data_type: ClassVar[Type[BaseModel]]

    @classmethod
    def concretize(cls, data_type: Type[BaseModel]):
        return type(f'Session{data_type.__name__}', (cls,), {'_data_type': data_type})

    def __init__(self, backend: SessionBackend, session_id: str = None):
        self.session_id = session_id
        self._backend = backend
        self.is_loaded = False
        self._is_modified = False
        self._init_data = None

    @property
    def is_empty(self) -> bool:
        return False

    @property
    def is_modified(self) -> bool:
        """Check if session data has been modified,"""
        return self._is_modified or self.is_loaded and self._data.dict() != self._init_data.dict()

    @property
    def data(self) -> DataType:
        if not self.is_loaded:
            raise SessionNotLoaded("Session is not loaded.")
        return self._data

    @data.setter
    def data(self, value: DataType) -> None:
        self._data = value
        if self._init_data is None:
            self._init_data = value.copy(deep=True)

    async def load(self) -> None:
        """Load data from the backend.
        Subsequent calls do not take any effect."""
        if self.is_loaded:
            return

        if not self.session_id:
            self.data = self._data_type()
        else:
            raw = await self._backend.read(self.session_id)
            self.data = self._data_type(**raw)

        self.is_loaded = True

    async def persist(self) -> str:
        self.session_id = await self._backend.write(self.data.dict(), self.session_id)
        return self.session_id

    async def delete(self) -> None:
        if self.session_id:
            self.data = self._data_type()
            await self._backend.remove(self.session_id)

    async def flush(self) -> str:
        await self.delete()
        return await self.regenerate_id()

    async def regenerate_id(self) -> str:
        self.session_id = await self._backend.generate_id()
        self._is_modified = True
        return self.session_id
