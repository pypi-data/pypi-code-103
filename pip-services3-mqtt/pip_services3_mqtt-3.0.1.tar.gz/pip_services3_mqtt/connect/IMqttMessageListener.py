# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import Any


class IMqttMessageListener(ABC):

    @abstractmethod
    def on_message(self, topic: str, message: Any, packet: Any):
        pass
