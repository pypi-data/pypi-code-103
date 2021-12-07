"""
API Contracts for DW Operation Sets
"""
from pydantic import BaseModel, Field
from typing import List, Optional

from pyrasgo.schemas import dw_operation as op_contracts
from pyrasgo.schemas import dataset as datasets_contracts


class OperationSetCreate(BaseModel):
    """
    Contract to create an operation set
    """
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.OperationCreate]]
    dataset_dependency_ids: Optional[List[int]] = Field(alias="datasetDependencyIds") # Dataset Ids

    class Config:
        allow_population_by_field_name = True


class OperationSetUpdate(BaseModel):
    """
    Contract to update an operation set
    """
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.OperationUpdate]]
    dataset_dependency_ids: Optional[List[int]] = Field(alias="datasetDependencyIds") # Dataset Ids

    class Config:
        allow_population_by_field_name = True


class OperationSet(BaseModel):
    """
    Contract to return from get endpoints
    """
    id: int
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.Operation]]
    dataset_dependencies: Optional[List[datasets_contracts.Dataset]] = Field(alias="datasetDependencies")
    organization_id: int = Field(alias="organizationId")

    class Config:
        allow_population_by_field_name = True
