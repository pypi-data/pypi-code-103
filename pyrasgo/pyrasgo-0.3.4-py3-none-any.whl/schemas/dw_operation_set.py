from pydantic import BaseModel
from typing import List, Optional

from pyrasgo.schemas.dw_operation import Operation
from pyrasgo.schemas.dataset import Dataset

class OperationSetCreate(BaseModel):
    operations: List[Operation]
    dependencies: Optional[List[Dataset]]


class OperationSet(OperationSetCreate):
    id: int
    operations: List[Operation]
    dependencies: Optional[List[Dataset]]
