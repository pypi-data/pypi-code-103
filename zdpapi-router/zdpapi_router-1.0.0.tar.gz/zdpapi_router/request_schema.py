from pydantic import BaseModel
from typing import List

class IdsSchema(BaseModel):
    """
    id列表
    """
    ids:List[int] = []