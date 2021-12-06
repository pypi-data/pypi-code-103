from _pytest.fixtures import _teardown_yield_fixture
from numpy.random.mtrand import noncentral_chisquare
from sqlalchemy.sql.expression import table
from .. import exceptions
from ..tracking.base.tracking_base import TrackingBase
from ..tracking.base.params import Params
from ..tracking import tracking_utils
from ..data.connector import PostgresHelper, AthenaHelper, TeradataHelper
from ..drift import data_drift_utils as drift_utils
import os
import pandas as pd
from typing import Iterable, List, Dict, Optional
import datetime
import time
import boto3
import joblib

from flyermlops import tracking


class FlightTracker(TrackingBase):
    def __init__(
        self,
        project_name=None,
        tracking_uri=None,
        tracking_schema=None,
        part_of_flight: bool = False,
        flight_tracking_id: str = None,
        *args,
        **kwargs,
    ):

        super().__init__(
            project_name=project_name,
            tracking_uri=tracking_uri,
            tracking_schema=tracking_schema,
            part_of_flight=part_of_flight,
            flight_tracking_id=flight_tracking_id,
            tracker_type="flight",
            *args,
            **kwargs,
        )

    def start_flight(self, engine: str = "postgres"):
        self.set_tracking_connection(engine)

    def set_tracking_connection(self, engine):
        super().set_tracking_connection(
            engine=engine,
            flight_tracking_id=self.flight_tracking_id,
            tracking_id=self.tracking_id,
        )

        return self.flight_tracking_id

    def end_flight(self):
        data = {"in_flight": 0}
        self.log_to_registry(data=data, tracking_id=self.flight_tracking_id)
        print(f"Flight {self.flight_tracking_id} is complete")

    def log_artifacts(
        self, key, value, tag=None,
    ):

        data = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "timestamp": time.time(),
            "flight_tracking_id": self.flight_tracking_id,
            "project_name": self.project_name,
            "key": key,
            "value": value,
            "tag": tag,
        }

        tracking_utils.log_registry_values(
            engine=self.tracking_engine,
            registry_schema=self.registries["tracker"],
            data=data,
        )

    def log_to_registry(self, data: dict, tracking_id):
        """Logs data features to data tracking_registry
        
        Args:
            feature_dict: Dictionary of features ({'feature name': feature type})
        """

        tracking_utils.log_registry_values(
            engine=self.tracking_engine,
            registry_schema=self.registries["flight"],
            data=data,
            tracking_id=tracking_id,
        )


class DataTracker(TrackingBase):
    def __init__(
        self,
        project_name=None,
        tracking_uri=None,
        tracking_schema=None,
        s3_bucket=None,
        part_of_flight: bool = False,
        log_data: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(
            project_name=project_name,
            tracking_uri=tracking_uri,
            tracking_schema=tracking_schema,
            part_of_flight=part_of_flight,
            s3_bucket=s3_bucket,
            tracker_type="data",
            *args,
            **kwargs,
        )

        self.log_data = log_data

        if log_data:
            self.set_tracking_connection()

    def set_tracking_connection(self, engine="postgres"):
        # Set tracking ids
        super().set_tracking_connection(
            engine=engine, flight_tracking_id=self.flight_tracking_id
        )

    def _set_storage_location(self):

        # Set buckets
        if self.s3_bucket is not None:
            bucket_prefix = None
            if self.project_name is not None:
                bucket_prefix = f"projects/{self.project_name}"
            if self.tracking_id is not None:
                if bucket_prefix is not None:
                    bucket_prefix = (
                        f"{bucket_prefix}/{self.tracking_id}/{self.tracker_type}"
                    )
                else:
                    bucket_prefix = f"{self.tracking_id}/{self.tracker_type}"

            elif self.tracking_id is None:
                if bucket_prefix is not None:
                    bucket_prefix = f"{bucket_prefix}/{self.tracker_type}"
                else:
                    bucket_prefix = f"{self.tracker_type}"

        self.bucket_prefix = bucket_prefix

        if self.log_data:
            tracking_utils.log_registry_values(
                engine=self.tracking_engine,
                registry_schema=self.registries["tracker"],
                data={"s3_location": f"{self.s3_bucket}/{self.bucket_prefix}"},
                tracking_id=self.tracking_id,
            )

    def set_data_connector(self, style, **kwargs):
        if style == "athena":
            self.athena_client = AthenaHelper(**kwargs)
            print("athena_client created")

        elif style == "teradata":
            self.teradata_client = TeradataHelper(**kwargs)
            print("teradata_client created")

        elif style == "postgres":
            self.postgres_client = PostgresHelper(**kwargs)
            print("postgres_client created")

    def log_features(self, feature_dict: dict):
        """Logs data features to data tracking_registry
        
        Args:
            feature_dict: Dictionary of features ({'feature name': feature type})
        """

        if type(feature_dict) is not dict:
            raise exceptions.NotofTypeDictionary(
                "A dictionary of feature names and types is expected"
            )

        data = {"feature_info": feature_dict}
        tracking_utils.log_registry_values(
            engine=self.tracking_engine,
            registry_schema=self.registries["tracker"],
            data=data,
            tracking_id=self.tracking_id,
        )

    def log_metrics(self, data: dict, tag: str = None):
        """Logs data metrics to data metrics registry
        
        Args:
            data: Dictionary of key, values ({'key': value}).
            tag: Optional tag to append to data dictionary.
        """

        values = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "project_name": self.project_name,
            "data_tracking_id": self.tracking_id,
        }

        print(data)
        for key, val in data.items():
            metrics = {
                "key": key,
                "value": val,
                "timestamp": int((time.time_ns()) / 1000000),
            }

            if tag is not None:
                metrics["tag"] = tag

            metadata = {**values, **metrics}
            tracking_utils.log_metrics(
                engine=self.tracking_engine,
                registry_schema=self.registries["metric"],
                data=metadata,
            )

    def run_drift_diagnostics(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        feature_mapping: dict = None,
        target_feature: str = None,
        current_label: str = "current",
        reference_label: str = "reference",
        log_data: bool = True,
        return_df: bool = False,
    ):

        """Computes drift diagnostics between reference and current data based upon column mapping
        
        Args:
            reference_data: Pandas dataframe of reference or background data to compare against.
            current_data: Pandas dataframe containing current data.
            column_mapping: Dictionary containing features (keys) and their column types.
            reference_label: Label for reference data.
            current_label: Label for current data.

        """

        # Compute feature drift
        feature_dict = {}

        if feature_mapping is None:
            feature_mapping = drift_utils.get_feature_types(dict(reference_data.dtypes))

        feature_list = feature_mapping.keys()

        # Create global model and compute feature importance
        feature_importance = drift_utils.compute_drift_feature_importance(
            reference_data,
            current_data,
            feature_list=feature_list,
            target_feature=target_feature,
        )

        if target_feature is not None:
            if not isinstance(target_feature, list):
                target_feature = [target_feature]
        else:
            target_feature = []

        for feature in [*feature_list, *target_feature]:
            feature_dict[feature] = dict.fromkeys(
                [
                    "type",
                    "intersection",
                    "missing_records",
                    "unique",
                    "reference_distribution",
                    "current_distribution",
                    "feature_importance",
                    "feature_auc",
                    "reference_label",
                    "current_label",
                    "target_feature",
                ]
            )

            feature_dict[feature]["type"] = feature_mapping[feature]

            # Subset data
            ref_data = reference_data[feature]
            cur_data = current_data[feature]

            # Create distributions and intersection between current and reference data
            results = drift_utils.compute_feature_stats(
                reference_data=ref_data,
                current_data=cur_data,
                reference_label=reference_label,
                current_label=current_label,
            )

            feature_dict[feature]["intersection"] = results["intersection"]
            feature_dict[feature]["missing_records"] = results["missing_records"]
            feature_dict[feature]["unique"] = results["unique"]

            feature_dict[feature]["feature_importance"] = feature_importance[feature][
                "feature_importance"
            ]
            feature_dict[feature]["feature_auc"] = feature_importance[feature][
                "feature_auc"
            ]

            feature_dict[feature]["reference_distribution"] = results[
                f"{reference_label}_histogram"
            ]
            feature_dict[feature]["current_distribution"] = results[
                f"{current_label}_histogram"
            ]

            feature_dict[feature]["reference_label"] = reference_label
            feature_dict[feature]["current_label"] = current_label

            if feature in target_feature:
                feature_dict[feature]["target_feature"] = 1

            else:
                feature_dict[feature]["target_feature"] = 0

        if log_data:
            dict_to_upload = {"drift_diagnostics": feature_dict}
            tracking_utils.log_registry_values(
                engine=self.tracking_engine,
                registry_schema=self.registries["tracker"],
                data=dict_to_upload,
                tracking_id=self.tracking_id,
            )

        if return_df:
            return (
                pd.DataFrame.from_dict(feature_dict, orient="index")
                .reset_index()
                .rename(columns={"index": "feature"})
            )

    def data_to_s3(self, data: pd.DataFrame, name: str):
        """
        Takes a pandas dataframe and writes a parquet file to s3.
        Write location: "s3://{s3_bucket}/{bucket_prefix}/{name}/".
        The S3 bucket and prefix are inferred from the instantiated Data Tracker.

        Args:
            data: Pandas dataframe to use to writing to parquet
            name: Name of specific s3 folder to write to
        """
        # Set storage location
        self._set_storage_location()
        self.set_data_connector(style="athena", **{"bucket": self.s3_bucket})
        bucket_prefix = f"{self.bucket_prefix}/{name}/{name}.parquet"
        self.athena_client.df_to_s3(data, bucket_prefix)

        print(
            f"Successfully saved data to s3://{self.s3_bucket}/{bucket_prefix}/{name}"
        )

    def read_s3_to_file(
        self,
        tracking_path: str,
        name: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ):
        """
        Reads a parquet file from a specified s3 tracking path.
        A name argument can be given to specify the folder in which to read data from
        in the tracking path.

        Args:
            tracking_path: S3 object path associated with a given tracking id
            name: Specific folder within the tracking path to read from. Optional
        """

        self.set_data_connector(style="athena", **{"bucket": self.s3_bucket})
        path = f"s3://{tracking_path}"
        if name is not None:
            path = f"{path}/{name}/"
        else:
            path = f"{path}/"
        df = self.athena_client.read_parquet(path, columns)
        return df


class ModelTracker(TrackingBase):
    def __init__(
        self,
        project_name=None,
        tracking_uri=None,
        tracking_schema=None,
        s3_bucket=None,
        part_of_flight: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(
            project_name=project_name,
            tracking_uri=tracking_uri,
            tracking_schema=tracking_schema,
            part_of_flight=part_of_flight,
            s3_bucket=s3_bucket,
            tracker_type="model",
            *args,
            **kwargs,
        )

    def set_tracking_connection(self, engine="postgres"):
        # Set tracking ids
        super().set_tracking_connection(
            engine=engine, flight_tracking_id=self.flight_tracking_id
        )

        # Set buckets
        if self.s3_bucket is not None:
            bucket_prefix = None
            if self.project_name is not None:
                bucket_prefix = f"projects/{self.project_name}"
            if self.tracking_id is not None:
                if bucket_prefix is not None:
                    bucket_prefix = (
                        f"{bucket_prefix}/{self.tracker_type}/{self.tracking_id}"
                    )
                else:
                    bucket_prefix = f"{self.tracker_type}/{self.tracking_id}"

        self.bucket_prefix = bucket_prefix

        tracking_utils.log_registry_values(
            engine=self.tracking_engine,
            registry_schema=self.registries["tracker"],
            data={"s3_location": f"{self.s3_bucket}/{self.bucket_prefix}"},
            tracking_id=self.tracking_id,
        )
