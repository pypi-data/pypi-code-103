import inspect
from functools import partial
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Generic, Iterator, NamedTuple, Optional, Tuple, TypeVar

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        pass

T = TypeVar('T')


class Notset:
    pass


class InjecterBase(Generic[T], metaclass=ABCMeta):
    def __init__(self, obj: T) -> None:
        self.obj = obj

    @abstractmethod
    def iter_field(self) -> Iterator[Tuple[str, Optional[Any]]]:
        """Iterate field names and default values
        """
        raise NotImplementedError()

    @abstractmethod
    def replace_field_values(self, fields: Dict[str, Any]) -> T:
        """Replace field value from dictionary.

        Parameters
        ----------
        fields : Dict[str, Any]
            Replacing dictionary
        """
        raise NotImplementedError()


class FunctionInjecter(InjecterBase):
    def __init__(self, obj: T) -> None:
        super().__init__(obj)
        self.argspec = inspect.getfullargspec(self.obj)

    def iter_field(self) -> Iterator[Tuple[str, Optional[Any]]]:
        defaults = self.argspec.defaults or []
        kwonlydefaults = self.argspec.kwonlydefaults or {}
        for arg in self.argspec.args[:-len(defaults)]:
            yield (arg, Notset)

        for arg, val in zip(
            self.argspec.args[-len(defaults):],
            defaults
        ):
            yield (arg, val)
        for arg, val in kwonlydefaults.items():
            yield arg, val

    def replace_field_values(self, fields: Dict[str, Any]) -> T:
        return partial(self.obj, **fields)


class ClassInjecter(FunctionInjecter):
    def __init__(self, obj: T) -> None:
        self.klass = obj
        super().__init__(obj.__init__)

    def replace_field_values(self, fields: Dict[str, Any]) -> T:
        return partial(self.klass, **fields)


class NamedtupleInjtecter(InjecterBase[NamedTuple]):
    def iter_field(self) -> Iterator[Tuple[str, Optional[Any]]]:
        for field in self.obj._fields[:-len(self.obj._field_defaults)]:
            yield field, Notset

        for field in self.obj._fields[-len(self.obj._field_defaults):]:
            yield field, self.obj._field_defaults[field]

    def replace_field_values(self, fields: Dict[str, Any]) -> T:
        return partial(self.obj, **fields)


class PydanticInjecter(InjecterBase[BaseModel]):
    def iter_field(self) -> Iterator[Tuple[str, Optional[Any]]]:
        for field, value in self.obj.__fields__.items():
            yield field, value.default

    def replace_field_values(self, fields: Dict[str, Any]) -> T:
        return partial(self.obj, **fields)


def create_injecter(t: type):
    if (
        hasattr(t, '_asdict')
        and hasattr(t, '_replace')
        and hasattr(t, '_fields')
        and hasattr(t, '_field_defaults')
    ):
        return NamedtupleInjtecter(t)
    elif isinstance(t, type) and issubclass(t, BaseModel):
        return PydanticInjecter(t)
    elif inspect.isclass(t):
        return ClassInjecter(t)
    else:
        try:
            return FunctionInjecter(t)
        except TypeError:
            raise TypeError(f'Unsupported callable type: {t}')
