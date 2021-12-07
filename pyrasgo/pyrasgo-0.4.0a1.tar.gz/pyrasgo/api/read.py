import pandas as pd
from typing import Dict, List, Optional

from .error import APIError
from pyrasgo import config
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, DataSource, Dataset


class Read():

    def __init__(self):
        from . import Get
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()

    def collection_data(self,
                        id: int,
                        filters: Optional[Dict[str, str]] = None,
                        limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Collection

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        collection = self.get.collection(id)
        if collection:
            try:
                table_metadata = collection._make_table_metadata()
                query, values = self.data_warehouse.make_select_statement(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Collection table is not reachable: {e}")
        raise APIError("Collection does not exist")

    def collection_snapshot_data(self,
                                 id: int,
                                 snapshot_index: int,
                                 filters: Optional[Dict[str, str]] = None,
                                 limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Collection Snapshot

        :param id: int
        :param snapshot_index: integer of the index
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned

        :return: Dataframe containing feature data
        """
        collection = self.get.collection(id)
        snapshot = self.get.collection_snapshot(id, snapshot_index)
        if snapshot:
            try:
                table_metadata = collection._make_table_metadata()
                table_metadata["table"] = snapshot['table_name']
                query, values = self.data_warehouse.make_select_statement(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Collection snapshot table is not reachable: {e}")
        raise APIError("Collection snapshot does not exist")

    def feature_data(self,
                     id: int,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Feature data

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        feature = self.get.feature(id)
        if feature.sourceTable:
            try:
                table_metadata = feature._make_table_metadata()
                #TODO: if we ever support multiple features, add them to this line -
                features = feature.columnName
                indices = ','.join(feature.indexFields)
                columns = indices +', '+features
                query, values = self.data_warehouse.make_select_statement(table_metadata, filters, limit, columns)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Feature table is not reachable: {e}")
        raise APIError("Feature table does not exist")

    def source_data(self,
                    id: int,
                    filters: Optional[Dict[str, str]] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo DataSource

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        data_source = self.get.data_source(id)
        if data_source:
            try:
                table_metadata = data_source._make_table_metadata()
                query, values = self.data_warehouse.make_select_statement(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"DataSource table is not reachable: {e}")
        raise APIError("DataSource does not exist")

    def dataset(self,
                    id: Optional[int] = None,
                    dataset: Optional[Dataset] = None,
                    filters: Optional[Dict[str, str]] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Dataset

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        if not dataset and id == None:
            raise ValueError(f"Must pass either a valid ID or Dataset object to read into a DataFrame")
        if not dataset:
            dataset = self.get.dataset(id)

        if dataset:
            dataset._require_operation_set()
            try:
                query, values = self.data_warehouse.make_select_statement({'fqtn': dataset.dw_table_name}, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Dataset table is not reachable: {e}")
        raise APIError("Dataset does not exist")