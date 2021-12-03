from pydantic import BaseModel
from typing import List, Dict, Optional

from pyrasgo.schemas.transform import Transform
from pyrasgo.schemas.dw_table import DataTableWithColumns

class OperationCreate(BaseModel):
    operation_name: str
    operation_args: Dict
    transform_id: int
    dw_table_id: int
    dw_operation_set_id: int
    transform: Optional[Transform]
    dw_table: Optional[DataTableWithColumns]
    dependencies: Optional[List[int]]


class Operation(OperationCreate):
    id: int
    operation_name: str
    operation_args: Dict
    transform_id: int
    dw_table_id: int
    dw_operation_set_id: int
    transform: Transform
    dw_table: Optional[DataTableWithColumns]
    dependencies: Optional[List[int]]
