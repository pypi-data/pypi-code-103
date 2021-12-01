from typing import Callable
from ..record import RouteRecord


Condition = Callable[[RouteRecord], bool]
