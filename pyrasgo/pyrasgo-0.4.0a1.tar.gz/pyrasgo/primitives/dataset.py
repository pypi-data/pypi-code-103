"""
Dataset 'Primitive' In rasgo SDK
"""
from typing import Dict, Optional, Union, List, Callable
import functools

import pandas as pd

from pyrasgo.api.connection import Connection
from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse
from pyrasgo.utils import naming
from pyrasgo.api.error import APIError
from pyrasgo import schemas

JSON_TYPES = Union[str, int, List, Dict]


def require_operation_set(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self: 'Dataset' = args[0]
        self._require_operation_set()
        return func(*args, **kwargs)
    return wrapper


class Dataset(Connection):
    """
    Representation of a Rasgo Dataset
    """

    def __init__(self,
                 # Args passed from Rasgo
                 api_dataset: Optional[schemas.Dataset] = None,
                 api_operation_set: Optional[schemas.OperationSet] = None,
                 # Args passed from transforming
                 operations: Optional[List[schemas.OperationCreate]] = None,
                 dataset_dependencies: Optional[List[int]] = None,
                 guid: Optional[str] = None,
                 **kwargs: Dict):
        """
        Init functions in two modes: 
            1. This Dataset retrieved from Rasgo. This object is for reference, and cannot 
               be changed, but can be transformed to build new datsets
            2. This Dataset represents a new datset under construction. It is not persisted in Rasgo 
               and instead consists of some operations that will be used to generate a new datset.
        """
        super().__init__(**kwargs)

        self._api_dataset: schemas.Dataset = api_dataset
        self._api_operation_set: schemas.OperationSet = api_operation_set
        self._operations = operations if operations else []
        self._dataset_dependencies = dataset_dependencies if dataset_dependencies else []
        self._guid = guid

    def __repr__(self) -> str:
        """
        Get string representation of this dataset
        """
        if self._api_dataset:
            return f"Dataset(id={self._api_dataset.id}, " \
                   f"name={self._api_dataset.name}, " \
                   f"status={self._api_dataset.status}, " \
                   f"description={self._api_dataset.description!r})"
        else:
            return f"Dataset()"

# ----------
# Properties
# ----------

    @property
    @require_operation_set
    def source_code(self, full=False) -> str:
        """
        Return the source code SQL used to generate this dataset

        full: return the full list of operations that create this dataset or just the last one
        """
        if (not hasattr(self._api_operation_set, "operations")) or (not self._api_operation_set.operations):
            return "No operations available for this dataset"
        if full:
            return '\n'.join([x.operation_sql for x in self._api_operation_set.operations])
        return self._api_operation_set.operations[-1].operation_sql

    @property
    def dw_table_name(self) -> str:
        """
        Get the table name for this Dataset, either as a table that exists in Rasgo,
        or the final table produced by this Dataset's operations.
        """
        if self._api_dataset and self._api_dataset.dw_table:
            return self._api_dataset.dw_table.fqtn
        elif self._guid:
            return self._guid
        raise AttributeError("No data warehouse table exists for this Dataset")

# --------
# Methods
# --------

    def transform(
            self,
            transform_name: str,
            arguments: Optional[Dict[str, Union[JSON_TYPES, 'Dataset']]] = None,
            operation_name: Optional[str] = None,
            **kwargs: Union[str, int, List, Dict, 'Dataset']
    ) -> 'Dataset':
        """
        Returns an new dataset with the referenced transform
        added to this dataset's definition/operation set
        """
        arguments = arguments if arguments else {}

        # Update the Transform arguments with any supplied kwargs
        arguments.update(kwargs)

        # Add required reference to self in transform
        arguments['source_table'] = self

        dataset_dependencies = self._dataset_dependencies
        operation_dependencies = [self.dw_table_name]
        parent_operations = []

        for k, v in arguments.items():
            if isinstance(v, self.__class__):
                if v._api_dataset:
                    v._check_can_transform()
                    dataset_dependencies.append(v._api_dataset.dw_table.id)
                else: 
                    # if parent (could be self) is another transformed dataset, grab it's operations too
                    parent_operations.extend(v._operations)
                arguments[k] = v.dw_table_name
                operation_dependencies.append(v.dw_table_name)

        # Init table name GUID for outputted dataset
        new_guid = naming.random_operation_table_name()
        transform = self._get_transform_by_name(transform_name)

        operation_create = schemas.OperationCreate(
            operation_name=operation_name if operation_name else transform.name,
            operation_args=arguments,
            transform_id=transform.id,
            table_name=new_guid,
            table_dependency_names=operation_dependencies
        )

        operations = parent_operations + [operation_create]

        return self.__class__(
            operations=operations,
            dataset_dependencies=dataset_dependencies,
            guid=new_guid,
        )

    @require_operation_set
    def read_into_df(self, filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Read this dataset into a dataframe
        """
        from pyrasgo.api import Read
        return Read().dataset(dataset=self, filters=filters, limit=limit)

    def preview(self) -> pd.DataFrame:
        """
        Get the top 10 rows of data for this dataset as a dataframe.
        """
        return self.read_into_df(limit=10)

# -----------------------------------------------------
# Methods requiring dataset to be registered with Rasgo
# -----------------------------------------------------

    def visualize(self) -> None:
        """
        Opens the visualization of this dataset in the Rasgo UI. Dataset must have been `saved` in Rasgo
        """
        raise NotImplementedError

    def profile(self) -> any:
        """
        Get stats for a dataset. Dataset must have been `saved` in Rasgo
        """
        raise NotImplementedError

# ---------------------------------
#  Private Helper Funcs for Class
# ---------------------------------

    def _get_transform_by_name(self, transform_name: str) -> schemas.Transform:
        """
        Get and return a transform obj by name

        Raise Error if no transform with that name found
        """
        from pyrasgo.api import Get
        get = Get()
        available_transforms = get.transforms()
        for transform in available_transforms:
            if transform_name == transform.name:
                return transform
        raise ValueError(f"No Transform found with name "
                         f"'{transform_name}' available in your organization")

    def _check_can_transform(self) -> None:
        if (self._api_dataset and not self._api_dataset.dw_table_id) or self._api_dataset.status != "published":
            raise APIError(
                f"Dataset({self._api_dataset.id}) has not been locked, and cannot be used in new dataset transformations")

    def _require_operation_set(self) -> None:
        """
        This function used to ensure that an operation set exists for a given dataset before 
        attempting to do any operations that require the operations to exist in Rasgo (for example,
        previewing tables before they actually exist)

        If the operation set does not exist, AND the set of operations to be created does, create the 
        operation set using those operation definitions. 
        """
        if not self._api_operation_set and self._operations:
            from pyrasgo.api.create import Create
            self._api_operation_set = Create()._operation_set(self._operations, self._dataset_dependencies)
