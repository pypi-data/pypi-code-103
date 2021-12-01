import sys
import pydantic
from typing import Union, Optional
sys.path.insert(1, '/app')


# noinspection PyCompatibility
class ConvexBaseData(pydantic.BaseModel):
    area_limit: Optional[Union[float, int]] = 250
    edge_limit: Optional[int] = 20
