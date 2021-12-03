from pydantic import BaseModel
from typing import Optional, List


class DataColumn(BaseModel):
    id: int
    columnName: str
    dataType: str


class DataTable(BaseModel):
    id: int
    tableName: str
    databaseName: str
    schemaName: str
    fqtn: Optional[str]


class DataTableWithColumns(BaseModel):
    id: int
    tableName: str
    databaseName: str
    schemaName: str
    fqtn: Optional[str]
    columns: Optional[List[DataColumn]]
