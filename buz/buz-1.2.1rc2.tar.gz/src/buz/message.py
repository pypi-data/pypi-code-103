from abc import ABC
from dataclasses import field, dataclass
from datetime import datetime
from typing import Any, ClassVar
from uuid import uuid4


@dataclass(frozen=True)
class Message(ABC):
    DATE_TIME_FORMAT: ClassVar[str] = "%Y-%m-%d %H:%M:%S.%f"

    id: str = field(init=False, default_factory=lambda: str(uuid4()))
    created_at: str = field(
        init=False, default_factory=lambda: datetime.strftime(datetime.now(), Message.DATE_TIME_FORMAT)
    )

    @classmethod
    def fqn(cls) -> str:
        return f"{cls.__module__}.{cls.__name__}"

    @classmethod
    def restore(cls, **kwargs: Any) -> "Message":  # type: ignore
        message_id = kwargs.pop("id")
        created_at = kwargs.pop("created_at")

        instance = cls(**kwargs)  # type: ignore

        object.__setattr__(instance, "id", message_id)
        object.__setattr__(instance, "created_at", created_at)
        return instance

    def parsed_created_at(self) -> datetime:
        return datetime.strptime(self.created_at, self.DATE_TIME_FORMAT)
