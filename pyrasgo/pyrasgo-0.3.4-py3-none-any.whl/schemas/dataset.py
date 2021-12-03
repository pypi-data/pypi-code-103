from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from pyrasgo.schemas.dataset_column import DatasetColumn
from pyrasgo.schemas.dw_table import DataTable

class Dataset(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    status: str
    owner_id: Optional[int]
    organization_id: int
    dw_table_id: int
    dw_operation_set_id: int
    columns: Optional[List[DatasetColumn]]
    dw_table: Optional[DataTable]
    consumer_count: int
    attributes: Optional[dict]
    tags: Optional[List[str]]
    create_timestamp: datetime
    create_author: int
    update_timestamp: datetime
    update_author: int


class DatasetBulk(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    owner_id: Optional[int]
    organization_id: int
    dw_table_id: int
    dw_table: Optional[DataTable]
    dw_operation_set_id: int
    column_count: int
    consumer_count: int
    create_timestamp: datetime
    create_author: int
    update_timestamp: datetime
    update_author: int


class DatasetCreate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    owner_id: Optional[int]
    organization_id: Optional[int]
    dw_table_id: Optional[int]
    dw_operation_set_id: Optional[int]
