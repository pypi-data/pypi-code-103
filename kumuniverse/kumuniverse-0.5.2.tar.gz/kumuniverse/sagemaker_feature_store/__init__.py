"""
Sagemaker Feature Store (SMFS) Module for accessing SMFS instance.
"""

import boto3
from botocore.config import Config
from pandas.core.frame import DataFrame
from sagemaker.feature_store.feature_definition import (
    FeatureTypeEnum,
    FractionalFeatureDefinition,
    IntegralFeatureDefinition,
    StringFeatureDefinition,
)
from sagemaker.session import Session
from sagemaker import get_execution_role
from sagemaker.feature_store.feature_group import AthenaQuery, FeatureGroup
from pyspark.sql import DataFrame as SparkDataFrame
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from typing import Union, List, Dict
import pandas as pd
import os
import time
import json


class SagemakerFeatureStore:
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region=None,
        arn_role=None,
    ):
        """
        Initializes the AWS Sagemaker Feature Store API.

        Parameters
        ----------
        aws_access_key_id : str, optional
            AWS access key credential (default is None)

        aws_secret_access_key : str, optional
            AWS secret access key credential (default is None)

        aws_region : str, optional
            AWS Region of credential (default is None)

        arn_role : str, optional
            Role for executing Feature Store API and commands (default is None)

        Attributes
        ----------
        sagemaker_client : any
            Sagemaker client connection

        runtime : any
            Sagemaker Feature Store runtime client connection

        session : Session object
            Sagemaker Feature Store session

        role : str
            AWS ARN role

        default_s3_bucket_name : str
            S3 bucket where the offline store data is stored

        athena_queries_prefix_uri : str
            S3 URI where offline store queries are stored
        """

        if not aws_region:
            # Sagemaker Notebook
            region = boto3.Session().region_name

            # Databricks Notebook
            if region is None:
                region = "ap-southeast-1"
        else:
            region = aws_region

        if aws_access_key_id and aws_secret_access_key and aws_region:
            boto_session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
            region = aws_region
        else:
            boto_session = boto3.Session(region_name=region)

        # Create sessions
        self.sagemaker_client = boto_session.client(
            service_name="sagemaker", region_name=region
        )
        self.runtime = boto_session.client(
            service_name="sagemaker-featurestore-runtime", region_name=region
        )
        self.session = Session(
            boto_session=boto_session,
            sagemaker_client=self.sagemaker_client,
            sagemaker_featurestore_runtime_client=self.runtime,
        )

        if not arn_role:
            # Working only on Sagemaker Notebooks
            # Please attach AmazonSageMakerFullAccess and AmazonSageMakerFeatureStoreAccess policies
            # arn:aws:iam::<id>:role/<role_name>
            self.role = get_execution_role()
        else:
            self.role = arn_role

        # Default variables
        self.default_s3_bucket_name = "kdp-sagemaker-feature-store"
        self.athena_queries_prefix_uri = "athena_queries"

    def add_event_time_column_df(
        self,
        data_frame: DataFrame,
        event_time_feature_name: str = "EventTime",
        timestamp: int = None,
    ):
        """
        Adds an event time column to a Pandas Dataframe

        Parameters
        ----------
        data_frame : DataFrame (Pandas), required
            Pandas DataFrame object to be used for adding the event time column

        event_time_feature_name : str, optional
            Name of the column

        timestamp : int, optional
            Unix timestamp in seconds


        Returns
        -------
        Pandas DataFrame
        """

        # Create EventTime column in unix
        current_time_sec = timestamp if timestamp else int(round(time.time()))

        data_frame[event_time_feature_name] = pd.Series(
            [current_time_sec] * len(data_frame), dtype="float64"
        )

        return data_frame

    def cast_object_to_string_df(self, data_frame: DataFrame):
        """
        Adds an event time column to a Pandas Dataframe

        Parameters
        ----------
        data_frame : DataFrame (Pandas), required
            Pandas DataFrame object to be used for casting object types to string


        Returns
        -------
        Pandas DataFrame
        """

        for label in data_frame.columns:
            if data_frame.dtypes[label] == "object":
                data_frame[label] = data_frame[label].astype("str").astype("string")

        return data_frame

    def create_feature_group(
        self,
        feature_group_name: str,
        features_info: List[Dict[str, Union[str, FeatureTypeEnum]]],
        record_identifier_feature_name: str,
        event_time_feature_name: str,
        enable_online_store: bool,
        enable_offline_store: bool,
        s3_uri_offline_store_output: str = None,
    ):
        """
        Creates a Feature Group in AWS Sagemaker Feature Store

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be created

        features_info : list[dict[str, [str, FeatureTypeEnum]]], required
            List of features/columns with their corresponding data types (STRING, FRACTIONAL, INTEGRAL)

        record_identifier_feature_name : str, required
            Record Identifier feature/column name for the Feature Group

        event_time_feature_name : str, required
            Event Time feature/column name for the Feature Group

        enable_online_store : bool, required
            For enabling online store

        enable_offline_store : bool, required
            For enabling offline store

        s3_uri_offline_store_output : str, optional
            S3 URI where you can keep offline store data, if none is specified, it will use the default S3 URI


        Returns
        -------
        None
        """

        if s3_uri_offline_store_output is None and enable_offline_store is True:
            s3_uri_offline_store_output = f"s3://{self.default_s3_bucket_name}"

        feature_definitions = self._feature_info_to_feature_definitions(
            features_info=features_info
        )

        feature_group = FeatureGroup(
            name=feature_group_name,
            sagemaker_session=self.session,
            feature_definitions=feature_definitions,
        )

        # Feature group creation
        feature_group.create(
            s3_uri=(
                s3_uri_offline_store_output if enable_offline_store is True else False
            ),
            record_identifier_name=record_identifier_feature_name,
            event_time_feature_name=event_time_feature_name,
            role_arn=self.role,
            enable_online_store=enable_online_store,
        )

        print(f'Creating "{feature_group_name}" Feature Group..')
        self._wait_for_feature_group_creation(feature_group)

    def get_feature_group(self, feature_group_name: str):
        """
        Retrieves the Feature Group Object

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be retrieved


        Returns
        -------
        Sagemaker Feature Group
        """

        return FeatureGroup(name=feature_group_name, sagemaker_session=self.session)

    def delete_feature_group(self, feature_group_name: str):
        """
        Deletes the Feature Group

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be deleted


        Returns
        -------
        None
        """

        try:
            feature_group = self.get_feature_group(feature_group_name)
            print(f'Deleting "{feature_group.name}" Feature Group..')
            feature_group.delete()
            self._wait_for_feature_group_deletion(feature_group)
        except Exception as err:
            raise Exception("ERROR - Delete Feature Group:", err)

    def get_online_features(
        self,
        feature_group_name: str,
        record_identifier: str,
        features_list: Union[list, None] = None,
    ):
        """
        Retrieves features of a single record identifier from the online store

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be retrieved

        record_identifier : str, required
            Record identifier name to be queried

        features_list : list | None, optional
            List of features/columns to be included in the query to online store

        Returns
        -------
        dict : Key-value pair where key is the feature name and value is the value as string
        """

        if features_list:
            record = self.runtime.get_record(
                FeatureGroupName=feature_group_name,
                RecordIdentifierValueAsString=record_identifier,
                FeatureNames=features_list,
            )["Record"]
        else:
            record = self.runtime.get_record(
                FeatureGroupName=feature_group_name,
                RecordIdentifierValueAsString=record_identifier,
            )["Record"]

        return self._reformat_to_dict(record)

    def get_batch_online_features(
        self,
        feature_group_name: str,
        record_identifiers_list: list,
        features_list: Union[list, None] = None,
    ):
        """
        Retrieves features of multiple record identifiers from the online store

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be retrieved

        record_identifiers_list : list, required
            List of record identifier names

        features_list : list | None, optional
            List of features/columns to be included in the query to online store

        Returns
        -------
        list[dict] : List of key-value pairs where key is the feature name and value is the value as string
        """

        def batch_get_record(identifiers_list: list):
            if features_list:
                return self.runtime.batch_get_record(
                    Identifiers=[
                        {
                            "FeatureGroupName": feature_group_name,
                            "RecordIdentifiersValueAsString": identifiers_list,
                            "FeatureNames": features_list,
                        },
                    ]
                )
            else:
                return self.runtime.batch_get_record(
                    Identifiers=[
                        {
                            "FeatureGroupName": feature_group_name,
                            "RecordIdentifiersValueAsString": identifiers_list,
                        },
                    ]
                )

        # Split into 100s
        item_per_chunk = 100
        chunks = [
            record_identifiers_list[x : x + item_per_chunk]
            for x in range(0, len(record_identifiers_list), item_per_chunk)
        ]

        # Execute in multithreads
        workers = len(chunks)
        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(batch_get_record, chunk) for chunk in chunks]
            for future in as_completed(futures):
                results.append(future.result())

        # Format results to a list of key-value pairs
        formatted_results = []
        for result in results:
            for record in result["Records"]:
                formatted_results.append(self._reformat_to_dict(record["Record"]))

        return formatted_results

    def ingest_pandas(
        self,
        feature_group_name: str,
        data_frame: DataFrame,
        max_workers: int = 1,
        max_processes: int = 1,
        wait: bool = True,
        timeout: Union[int, float, None] = None,
    ):
        """
        Ingests Pandas DataFrame into the Feature Group

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        data_frame : DataFrame (Pandas), required
            Pandas DataFrame to be ingested

        max_workers : int, optional
            Number of threads that will be created to work on different partitions of the data_frame in parallel

        max_processes : int, optional
            Number of processes that will be created to work on different partitions of the data_frame in parallel, each with max_worker threads.

        wait : bool, optional
            Whether to wait for the ingestion to finish or not

        timeout : int, optional
            `concurrent.futures.TimeoutError` will be raised if timeout is reached

        Returns
        -------
        None
        """

        feature_group = self.get_feature_group(feature_group_name)
        feature_definitions = feature_group.describe().get("FeatureDefinitions")
        print(f'\nStarted ingesting data for "{feature_group_name}"..')
        print(f'\n"{feature_group_name}" Feature Definitions:\n{feature_definitions}')
        feature_group.ingest(
            data_frame=data_frame,
            max_workers=max_workers,
            max_processes=max_processes,
            wait=wait,
            timeout=timeout,
        )
        if wait:
            print(f'\nSuccessfully inserted data to "{feature_group_name}"')
        else:
            print(
                f'\nInserting data to "{feature_group_name}" is running in background..'
            )

    def ingest_spark_df(
        self,
        feature_group_name: str,
        paritioned_spark_df: SparkDataFrame,
    ):
        """
        Ingests a partitioned Spark DataFrame into the Feature Group.
        Runs a `foreachPartition()` method to the partitioned dataframe to parallelize ingestion

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        paritioned_spark_df : DataFrame (Spark), required
            List of record identifier names

        Returns
        -------
        None
        """

        def ingest_parallelize_spark_df(feature_group_name, rows):
            rows = list(rows)
            region = "ap-southeast-1"
            os.environ["AWS_DEFAULT_REGION"] = region
            session = boto3.session.Session()
            runtime = session.client(
                service_name="sagemaker-featurestore-runtime",
                config=Config(retries={"max_attempts": 10, "mode": "standard"}),
            )
            for _, row in enumerate(rows):
                record = [
                    {"FeatureName": column, "ValueAsString": str(row[column])}
                    for column in row.__fields__
                    if row[column] is not None
                    and row[column] != ""
                    and row[column] != 0.0
                ]
                resp = runtime.put_record(
                    FeatureGroupName=feature_group_name, Record=record
                )
                if not resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    raise (f"PutRecord failed: {resp}")
            return

        print(f'Ingesting Spark Dataframe to "{feature_group_name}" Feature Store..')
        try:
            paritioned_spark_df.foreachPartition(
                lambda rows: ingest_parallelize_spark_df(feature_group_name, rows)
            )
        except Exception as e:
            raise Exception("ERROR:", e)

    def _feature_info_to_feature_definitions(
        self, features_info: List[Dict[str, Union[str, FeatureTypeEnum]]]
    ):
        """
        Converts a list of features info to AWS feature definitions format

        Parameters
        ----------
        features_info : list[dict[str, [str, FeatureTypeEnum]]], required
            List of features/columns with their corresponding data types (STRING, FRACTIONAL, INTEGRAL)

        Returns
        -------
        list
        """

        feature_definitions = []
        for feature in features_info:
            if feature["FeatureType"] == FeatureTypeEnum.FRACTIONAL:
                feature_definitions.append(
                    FractionalFeatureDefinition(feature["FeatureName"])
                )
            elif feature["FeatureType"] == FeatureTypeEnum.INTEGRAL:
                feature_definitions.append(
                    IntegralFeatureDefinition(feature["FeatureName"])
                )
            else:
                feature_definitions.append(
                    StringFeatureDefinition(feature["FeatureName"])
                )
        return feature_definitions

    def get_offline_features(
        self,
        query_string: str,
        athena_query_instance: AthenaQuery,
        s3_output_location: str,
        wait: bool = True,
    ):
        """
        Retrieves features from the offline store via Athena Query

        Parameters
        ----------
        query_string : str, required
            Amazon Athena query string

        athena_query_instance : AthenaQuery, required
            Athena Query instance retrieved from a Sagemaker Feature Group

        s3_output_location : str, required
            S3 URI to upload offline query outputs

        wait : str, required
            Whether to wait for the query to finish or not

        Returns
        -------
        None
        """

        athena_query_instance.run(
            query_string=query_string, output_location=s3_output_location
        )

        if wait is True:
            athena_query_instance.wait()
            return athena_query_instance.as_dataframe()
        else:
            return athena_query_instance

    def describe_feature_group(self, feature_group_name: str, features=None):
        """
        Gets the information about a specific feature group.

        Parameters
        ----------
        feature_group_name : str, required
            Name of the feature group to be described

        features : list, not required
            Feature keys that will be shown
                Default : FeatureGroupName, FeatureDefinitions, FeatureGroupStatus, EventTimeFeatureName, OfflineStoreConfig, OnlineStoreConfig, RecordIdentifierFeatureName

        Example ::
            ("customers-feature-group-16-07-38-24", ['FeatureGroupName', 'FeatureDefinitions'])

        Returns
        -------
        JSON object
        """
        if features is None:
            features = [
                "FeatureGroupName",
                "FeatureDefinitions",
                "FeatureGroupStatus",
                "EventTimeFeatureName",
                "OfflineStoreConfig",
                "OnlineStoreConfig",
                "RecordIdentifierFeatureName",
            ]

        print("\nFEATURE GROUP:", feature_group_name)
        feature_group = self.get_feature_group(feature_group_name)
        custom_feature = {
            feature_key: feature_group.describe()[feature_key]
            for feature_key in features
        }
        print(json.dumps(custom_feature, indent=2, default=str))

    def get_feature_groups_list(self):
        """
        Lists all the feature groups in the feature store

        Returns
        -------
        None
        """

        print("LIST OF FEATURE GROUPS:")
        for group in self.sagemaker_client.list_feature_groups(MaxResults=100)[
            "FeatureGroupSummaries"
        ]:
            print(group["FeatureGroupName"])

    def _reformat_to_dict(self, record: dict):
        """
        Reformats output of `get_record()` API to key-value pair

        Parameters
        ----------
        record : dict, required
            Resulting record from Sagemaker Feature Store `get_record()` API

        Returns
        -------
        dict : Key-value pair where key is the feature name and value is the value as string
        """

        formatted_record = {}
        for item in record:
            key = item["FeatureName"]
            value = item["ValueAsString"]
            formatted_record[key] = value

        return formatted_record

    def _wait_for_feature_group_creation(self, feature_group: FeatureGroup):
        """
        Continuously check if Feature Group is created

        Parameters
        ----------
        feature_group : FeatureGroup, required
            Sagemaker Feature Group object

        Returns
        -------
        None
        """

        status = feature_group.describe().get("FeatureGroupStatus")
        while status == "Creating":
            print("Waiting for Feature Group Creation")
            time.sleep(3)
            status = feature_group.describe().get("FeatureGroupStatus")
        if status != "Created":
            raise
            raise RuntimeError(f"Failed to create feature group {feature_group.name}")
        print(f"FeatureGroup {feature_group.name} successfully created.")

    def _wait_for_feature_group_deletion(self, feature_group):
        """
        Continuously check if Feature Group is deleted

        Parameters
        ----------
        feature_group : FeatureGroup, required
            Sagemaker Feature Group object

        Returns
        -------
        None
        """

        status = feature_group.describe().get("FeatureGroupStatus")
        while status == "Deleting":
            print("Waiting for Feature Group Deletion")
            time.sleep(3)
            try:
                status = feature_group.describe().get("FeatureGroupStatus")
            except Exception:
                print(f"FeatureGroup {feature_group.name} successfully deleted.")
                break
        if status == "DeleteFailed":
            raise RuntimeError(f"Failed to delete feature group {feature_group.name}")


if __name__ == "__main__":
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    role = "arn:aws:iam::137071197966:role/kdp-sagemaker-feature-store"
    feature_store = SagemakerFeatureStore(
        aws_access_key_id, aws_secret_access_key, "ap-southeast-1", role
    )

    # features_list = ["streamer_id", "cover_photo_embedding"]
    # raw_data = feature_store.get_online_features(
    #     "streamers-cpce-fg-11-06-54-38", "cpce:6WEL21LZxiyBQ78q"
    # )
    # print(json.dumps(raw_data, indent=2))

    # feature_group_name = "kumuniverse-fg-test"

    # Feature Group Creation Example
    # Prepare Pandas dataset for ingestion
    # record_identifier_feature_name = "streamer_id"
    # event_time_feature_name = "EventTime"

    # df = pd.read_csv("streamers_cpce.csv")
    # df.drop(columns=["expiry", "updated_at"], inplace=True)
    # df = feature_store.add_event_time_column_df(
    #     data_frame=df, event_time_feature_name=event_time_feature_name
    # )
    # df = feature_store.cast_object_to_string_df(df)
    # print(df.info())

    # features_info = [
    #     {"FeatureName": "streamer_id", "FeatureType": FeatureTypeEnum.STRING},
    #     {"FeatureName": "cover_photo_embedding", "FeatureType": FeatureTypeEnum.STRING},
    #     {"FeatureName": "streamer_feature", "FeatureType": FeatureTypeEnum.STRING},
    #     {"FeatureName": "tag_embedding", "FeatureType": FeatureTypeEnum.STRING},
    #     {"FeatureName": "EventTime", "FeatureType": FeatureTypeEnum.FRACTIONAL},
    # ]
    # feature_store.create_feature_group(
    #     feature_group_name=feature_group_name,
    #     features_info=features_info,
    #     record_identifier_feature_name="streamer_id",
    #     event_time_feature_name=event_time_feature_name,
    #     enable_online_store=True,
    #     enable_offline_store=True,
    # )

    # # Describe Feature Group
    # feature_group = feature_store.get_feature_group(feature_group_name)
    # print("\n\n", json.dumps(feature_group.describe(), indent=4, default=str))

    # # Ingest Pandas Dataframe
    # feature_store.ingest_pandas(
    #     feature_group_name=feature_group_name, data_frame=df, max_workers=4
    # )

    # # Get Online Features by Single ID
    # features_list = ["streamer_id", "cover_photo_embedding"]

    # t0 = time.time()
    # raw_data = feature_store.get_online_features(
    #     feature_group_name, "cpce:6WEL21LZxiyBQ78q"
    # )
    # raw_data = feature_store.get_online_features(
    #     "v3-cross-test-14", "112VRJCR76KZKVMG#%crpZK4317791xTQy"
    # )
    # print(raw_data)
    # t1 = time.time()
    # total = t1 - t0
    # print("Single Query Time Execution:", round(total * 1000))

    # # # For Readability convert to Dataframe
    # print(raw_data)
    # data = pd.DataFrame.from_dict([raw_data])
    # print(data.head())
    # print(data.info())

    # # Get Online Features by Multiple IDs
    # streamers = df["streamer_id"].tolist()
    # features_list = ["streamer_id", "cover_photo_embedding"]
    # t0 = time.time()
    # results = feature_store.get_batch_online_features(
    #     feature_group_name, streamers, features_list
    # )
    # print("\nColumns:", results[0].keys())
    # print("Results Count:", len(results))
    # t1 = time.time()
    # total = t1 - t0
    # print("Concurrent Futures Time Execution:", round(total * 1000))

    # WARNING: It takes time to ingest data to the offline store as it converts it into parquet files
    # might need to wait a few minutes..
    # time.sleep(5)

    # Offline Store Query Example
    # feature_group = feature_store.get_feature_group(feature_group_name)
    # fg_query_instance = feature_group.athena_query()
    # fg_table = fg_query_instance.table_name
    # s3_output_loc = f"s3://{feature_store.default_s3_bucket_name}/{feature_store.athena_queries_prefix_uri}/"

    # query_string = f'SELECT * FROM "{fg_table}"'
    # print(query_string)

    # training_df = feature_store.get_offline_features(
    #     query_string, fg_query_instance, s3_output_loc
    # )
    # print(training_df.info())
    # print(training_df.head())
    # print(training_df.iloc[0])

    # List Feature Groups
    # feature_store.get_feature_groups_list()

    # Describe feature group
    # feature_store.describe_feature_group("v3-cross-test")

    # # # Delete Feature Groups
    # to_be_deleted = [
    #     "kumuniverse-fg-test-v9",
    #     "kumuniverse-fg-test-v10",
    #     "kumuniverse-fg-test-v11",
    #     "kumuniverse-fg-test-v8",
    # ]
    # for fg in to_be_deleted:
    #     feature_store.delete_feature_group(fg)

    # # List Feature Groups
    # for group in feature_store.sagemaker_client.list_feature_groups(MaxResults=100)[
    #     "FeatureGroupSummaries"
    # ]:
    #     print(group["FeatureGroupName"])

    # features_info = [
    #     # identifiers
    #     {"FeatureName": "vs_cross_id", "FeatureType": FeatureTypeEnum.STRING},
    #     {"FeatureName": "event_time", "FeatureType": FeatureTypeEnum.FRACTIONAL},
    #     # follow
    #     {"FeatureName": "vs_is_followed", "FeatureType": FeatureTypeEnum.STRING},
    #     # cross watch duration/count
    #     {
    #         "FeatureName": "vs_watch_count_day",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_avg_watch_duration_day",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_max_watch_duration_day",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_median_watch_duration_day",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_watch_count_3days",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_avg_watch_duration_3days",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_max_watch_duration_3days",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_median_watch_duration_3days",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_watch_count_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_avg_watch_duration_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_max_watch_duration_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_median_watch_duration_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_watch_count_month",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_avg_watch_duration_month",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_max_watch_duration_month",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_median_watch_duration_month",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_watch_count_3months",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_avg_watch_duration_3months",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_max_watch_duration_3months",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_median_watch_duration_3months",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     # cross rate features
    #     {
    #         "FeatureName": "vs_click_rate_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_comment_rate_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_share_rate_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     # more cross count
    #     {
    #         "FeatureName": "vs_list_click_count_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_share_count_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    #     {
    #         "FeatureName": "vs_comment_count_week",
    #         "FeatureType": FeatureTypeEnum.FRACTIONAL,
    #     },
    # ]

    # feature_group_name = "v3-cross-test-8"
    # record_identifier = "vs_cross_id"
    # event_time_identifier = "event_time"
    # feature_store.create_feature_group(
    #     feature_group_name=feature_group_name,
    #     features_info=features_info,
    #     record_identifier_feature_name=record_identifier,
    #     event_time_feature_name=event_time_identifier,
    #     enable_online_store=True,
    #     enable_offline_store=True,
    # )
