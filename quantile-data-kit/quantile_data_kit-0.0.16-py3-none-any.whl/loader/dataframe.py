from typing import Any, Dict, Union

import dask.dataframe as dd
import pandas as pd
from dagster import Field, OutputDefinition, Permissive
from qdk.base import BaseComponent
from qdk.dagster_types import DataFrameType
from qdk.s3_connection import S3Connection


class DataFrameLoader(BaseComponent):
    compute_function = "load"
    tags = {
        "kind": "loader",
    }
    input_defs = []
    output_defs = [
        OutputDefinition(DataFrameType, "df"),
    ]
    config_schema = {
        "uri": Field(
            str,
            description="The uri to load the dataframe from.",
        ),
        "use_dask": Field(
            bool,
            default_value=False,
            description="Whether to load the dataframe using Dask.",
        ),
        "repartitions": Field(
            int,
            is_required=False,
            description="How many partitions to create.",
        ),
        "drop_na": Field(
            bool,
            default_value=False,
            description="Whether to drop rows with missing values.",
        ),
        "load_params": Field(
            Permissive({}),
            description="Extra parameters that get passed to the loading function.",
        ),
    }

    @classmethod
    def load(
        cls,
        uri: str,
        use_dask: bool = False,
        repartitions: int = None,
        drop_na: bool = False,
        load_params: Dict[str, Any] = {},
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        # Choose which framework to use for loading the data
        framework = dd if use_dask else pd

        # Inject S3 connection information into the load parameters
        # if the uri starts with an S3 connection indicator
        if uri.startswith("s3://"):
            s3_connection = S3Connection()
            load_params = {
                "storage_options": {
                    "client_kwargs": {
                        "aws_access_key_id": s3_connection.aws_access_key_id,
                        "aws_secret_access_key": s3_connection.aws_access_secret_key,
                        "endpoint_url": s3_connection.aws_endpoint_url,
                    }
                },
                **load_params,
            }

        if uri.endswith(".csv"):
            df = framework.read_csv(
                uri,
                **load_params,
            )

        if uri.endswith(".parquet"):
            df = framework.read_parquet(
                uri,
                **load_params,
            )

        elif (
            uri.endswith(".json")
            or uri.endswith(".jsonl")
            or uri.endswith(".jsonlines")
        ):
            df = framework.read_json(
                uri,
                orient="records",
                lines=True,
                **load_params,
            )

        elif uri.endswith(".pkl"):
            df = pd.read_pickle(
                uri,
                **load_params,
            )

            if use_dask:
                df = dd.from_pandas(
                    df,
                    npartitions=repartitions,
                )

        # If using dask and repartitions are supplied
        if use_dask and repartitions is not None:
            df = df.repartition(npartitions=repartitions)

        # Drop rows with missing values
        if drop_na:
            df = df.dropna()
            df = df.reset_index(drop=True)

        return df
