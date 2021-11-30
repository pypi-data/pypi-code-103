from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel


class EventProperties(BaseModel, ABC):
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def __new_(self):
        if self is EventProperties:
            raise TypeError("Can't instantiate abstract class {}".format(EventProperties.__name__))
        return super(EventProperties, self).__new__(self)


class AnalyticsEvent(ABC):
    @abstractmethod
    def __init__(
        self, user_id, event_name, description, event_properties: EventProperties = None
    ) -> None:
        self.user_id = user_id
        self.event_name = event_name
        self.description = description
        self.event_properties = event_properties

# class AnalyticsEvent(BaseModel):
#     # @abstractmethod
#     # def __init__(
#     #     self, user_id, event_name, description, event_properties: EventProperties = None
#     # ) -> None:
#     #     self.user_id = user_id
#     #     self.event_name = event_name
#     #     self.description = description
#     #     self.event_properties = event_properties
#     user_id: Optional[str] = None
#     event_name: Optional[str] = None
#     description: Optional[str] = None
#     event_properties: Optional[EventProperties] = []

class Reveals(BaseModel):
    user_id: Optional[str] = None
