from pydantic import BaseModel
from typing import Optional


class DatasetColumn(BaseModel):
    id: int
    name: str
    display_name: Optional[str]
    data_type: str
    description: Optional[str]
    is_feature: bool
    is_dimension: bool
    dataset_id: int
    dw_column_id: int


class DatasetColumnCreate(BaseModel):
    name: str
    dispay_name: Optional[str]
    data_type: str
    description: Optional[str]
    is_feature: bool
    is_dimension: bool
    dataset_id: int
    dw_column_id: int
