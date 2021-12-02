from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseContext(ABC):
    @abstractmethod
    def get_all_values(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_value(self, key: str) -> Any:
        pass

    @abstractmethod
    def set_value(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def delete_value(self, key: str) -> None:
        pass

    @abstractmethod
    def clean(self):
        pass
