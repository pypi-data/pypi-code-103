# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import os
import sys
import time
import uuid
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

from ibm_wos_utils.fairness.batch.utils import constants
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob


class GroupBiasComputationJob(AIOSBaseJob):

    def __init__(self, arguments, job_name):
        """
        Constructor for the job class.
        :arguments: The arguments to the Spark job.
        """
        super().__init__(arguments)
        self.name = job_name

    def calculate_group_bias(self, data: DataFrame, inputs: dict, data_types: dict, model_type: str) -> dict:
        """
        The Spark job which calculates the disparate impact ratio and publishes the fairness metrics for the payload and their corresponding perturbed data.
        :data: The spark data frame containing the payload data.
        :inputs: The inputs dictionary.
        :data_types: The dictionary containing data types of all the fairness attributes.
        :model_type: The model type.
        """
        # First calculating the disparate impact on the payload data
        di_dict = BatchUtils.calculate_di_dict(
            data, inputs, data_types, model_type)
        return di_dict

    def run_job(self) -> None:
        """
        The entry point method for the Spark job.
        """
        start_time = time.time()

        try:
            # Reading the inputs from the argument list
            subscription = self.arguments["subscription"]
            monitor_instance = self.arguments["monitor_instance"]
            output_file_path = self.arguments["output_file_path"]

            if self.storage_type != "hive":
                raise Exception("Only Hive storage type is supported.")

            # Getting the inputs dictionary
            inputs = BatchUtils.get_inputs_from_monitor_instance(
                monitor_instance)
            min_records = get(monitor_instance,
                              "entity.parameters.min_records")

            # Getting the payload logging data source
            pl_data_source = BatchUtils.get_data_source_from_subscription(
                subscription, "payload")
            db_name = get(pl_data_source, "database_name")
            pl_table_name = get(pl_data_source, "table_name")

            # Reading the data
            df_spark, borrow_if_needed = self._read_data(
                subscription, monitor_instance, db_name, pl_table_name)

            # Getting the model type and the data types of the fairness attributes
            model_type = get(subscription, "entity.asset.problem_type")
            data_types = BatchUtils.get_data_types(
                subscription, inputs["fairness_attributes"])

            di_dict = self.calculate_group_bias(
                df_spark, inputs, data_types, model_type)
            rows_analyzed = get(di_dict, "rows_analyzed")

            if borrow_if_needed and rows_analyzed < min_records and rows_analyzed != 0:
                # Getting the last processed time
                last_processed_time = get(
                    monitor_instance, "entity.parameters.last_processed_ts")

                # Getting the timestamp column name
                output_data_schema = get(
                    subscription, "entity.asset_properties.output_data_schema")
                timestamp_column = BatchUtils.get_name_with_modeling_role(
                    constants.TIMESTAMP_MODELING_ROLE, output_data_schema)

                # Reading the borrowed records
                borrowed_df = self._read_borrowed_data(
                    db_name, pl_table_name, min_records - rows_analyzed, timestamp_column, last_processed_time)

                # Calculating DI variables on borrowed records
                borrowed_di_dict = self.calculate_group_bias(
                    borrowed_df, inputs, data_types, model_type)

                # Merging the DI values
                di_dict = BatchUtils.merge_di_dicts(di_dict, borrowed_di_dict)

            end_time = time.time()
            time_taken = end_time - start_time

            output_json = None
            # Checking if enough records were present
            if min_records:
                rows_analyzed = get(di_dict, "rows_analyzed")
                if rows_analyzed < min_records:
                    # Not enough records present in the PL table
                    output_json = {
                        "job_output": [
                            {
                                "data_name": "payload",
                                "time_taken": time_taken
                            }
                        ]
                    }

            if output_json is None:
                # Building the output JSON
                output_json = {
                    "job_output": [
                        {
                            "data_name": "payload",
                            "counts": di_dict,
                            "time_taken": time_taken
                        }
                    ]
                }

            # Converting the value of outermost value as string because of #19045
            output_json["job_output"] = json.dumps(output_json["job_output"])

            # Write to HDFS
            output_file_name = "{}.json".format(self.name)
            output_path = "{}/{}".format(output_file_path, output_file_name)
            self.save_data(path=output_path, data_json=output_json)
            return
        except Exception as ex:
            self.save_exception_trace(str(ex))
            raise ex

    def _read_data(self, subscription: dict, monitor_instance: dict, db_name: str, table_name: str) -> DataFrame:
        """
        Reads and returns data frame for group bias computation.
        :subscription: The subscription object.
        :monitor_instance: The monitor instance object.
        :db_name: The database name.
        :table_name: The table name.

        :returns: The data and a flag indicating if records are to be borrowed if required.
        """
        df = None
        borrow_if_needed = False

        # Setting the current database
        self.spark.catalog.setCurrentDatabase(db_name)

        # Checking if record timestamp column is present in the PL table
        output_data_schema = get(
            subscription, "entity.asset_properties.output_data_schema")
        timestamp_present = BatchUtils.check_if_modeling_role_present(
            constants.TIMESTAMP_MODELING_ROLE, output_data_schema)

        if not timestamp_present:
            # Raise an exception as the timestamp column is mandatory because of #19570
            raise Exception(
                "Mandatory timestamp column is not present in the schema!")

        # Getting the min records
        min_records = get(monitor_instance, "entity.parameters.min_records")

        # Building the SQL query for reading data
        read_data_sql = None
        if timestamp_present:
            # Checking the last processed time
            last_processed_time = get(
                monitor_instance, "entity.parameters.last_processed_ts")
            # Converting the last processed time into the format supported by Hive `%Y-%m-%d %H:%M:%S.%f`
            last_processed_time = DateUtil.get_datetime_as_str(DateUtil.get_datetime_str_as_time(
                str_time=last_processed_time), format="%Y-%m-%d %H:%M:%S.%f") if last_processed_time else None
            # Getting the timestamp column name
            timestamp_column = BatchUtils.get_name_with_modeling_role(
                constants.TIMESTAMP_MODELING_ROLE, output_data_schema)
            if min_records:
                if last_processed_time:
                    # This is not the first run
                    read_data_sql = "select * from {} where {} >= '{}'".format(
                        table_name, timestamp_column, last_processed_time)
                    borrow_if_needed = True
                else:
                    # This is the first run
                    read_data_sql = "select * from {}".format(table_name)
            else:
                # Reading the data from last processed time
                if last_processed_time:
                    # This is not the first run
                    read_data_sql = "select * from {} where {} >= '{}'".format(
                        table_name, timestamp_column, last_processed_time)
                else:
                    # This is the first run
                    read_data_sql = "select * from {}".format(table_name)
        # This code would be made reachable once #19570 is implemented
        """
        else:
            # ------------
            if min_records is None:
                # When both min records and record-timestamp column is not present
                read_data_sql = "select * from {}".format(table_name)
            else:
                # This case is handled at the configuration level,
                # we throw an error in this case
                pass
            # ------------
        """
        df = self.spark.sql(read_data_sql) if read_data_sql else None
        return df, borrow_if_needed

    def _read_borrowed_data(self, db_name: str, table_name: str, num_records: int, timestamp_column: str, last_processed_time: str) -> DataFrame:
        """
        Reads and returns the latest borrowed records older than last processed time.
        :db_name: The database name.
        :table_name: The table name.
        :num_records: The number of records to be read.
        :timestamp_column: The timestamp column in the table.
        :last_processed_time: The last processed time for fairness.
        """
        df = None

        # Setting the current database
        self.spark.catalog.setCurrentDatabase(db_name)

        # Converting the last processed time into the format supported by Hive `%Y-%m-%d %H:%M:%S.%f`
        last_processed_time = DateUtil.get_datetime_as_str(DateUtil.get_datetime_str_as_time(
            str_time=last_processed_time), format="%Y-%m-%d %H:%M:%S.%f") if last_processed_time else None

        # Building the SQL query and reading the data
        read_data_sql = "select * from {} where {} < '{}' order by {} desc limit {}".format(
            table_name, timestamp_column, last_processed_time, timestamp_column, num_records)
        df = self.spark.sql(read_data_sql)

        return df
