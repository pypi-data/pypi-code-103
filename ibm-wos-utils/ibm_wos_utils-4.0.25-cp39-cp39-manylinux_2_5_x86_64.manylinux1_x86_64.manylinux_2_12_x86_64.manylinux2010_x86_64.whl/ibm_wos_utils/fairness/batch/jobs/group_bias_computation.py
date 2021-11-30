# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import os
import sys
import time
import uuid
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.constants import PROBABILITY_MODELING_ROLE, RECORD_ID_MODELING_ROLE, REGRESSION_MODEL_TYPE, SUPPORTED_STORAGE_TYPES, TIMESTAMP_MODELING_ROLE
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class GroupBiasComputationJob(AIOSBaseJob):

    def __init__(self, arguments, job_name):
        """
        Constructor for the job class.
        :arguments: The arguments to the Spark job.
        """
        super().__init__(arguments)
        self.name = job_name

    def calculate_group_bias(self, data, inputs: dict, data_types: dict, model_type: str) -> dict:
        """
        The Spark job which calculates the disparate impact ratio and publishes the fairness metrics for the payload and their corresponding perturbed data.
        :data: The spark data frame containing the payload data. (from pyspark.sql.dataframe import DataFrame)
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
        self.logger.info("Started the group bias computation job run.")
        start_time = time.time()

        try:
            # Reading the inputs from the argument list
            subscription = self.arguments["subscription"]
            monitor_instance = self.arguments["monitor_instance"]
            output_file_path = self.arguments["output_file_path"]
            copy_measurement = False

            if self.storage_type not in SUPPORTED_STORAGE_TYPES:
                raise Exception("{} storage type is not supported. Supported storage types are {}".format(self.storage_type, SUPPORTED_STORAGE_TYPES))

            # Getting the inputs dictionary
            inputs = BatchUtils.get_inputs_from_monitor_instance(
                monitor_instance)
            
            # Adding the class label in inputs dictionary
            inputs["class_label"] = BatchUtils.get_name_with_modeling_role("prediction", get(subscription, "entity.asset_properties.output_data_schema"))
            min_records = get(monitor_instance,
                              "entity.parameters.min_records")

            # Getting the payload logger data source
            pl_data_source = BatchUtils.get_data_source_from_subscription(
                subscription, "payload")
            db_name = get(pl_data_source, "database_name")
            pl_table_name = get(pl_data_source, "table_name")
            pl_schema_name = get(pl_data_source, "schema_name")

            # Reading the data
            df_spark, borrow_if_needed = self._read_data(
                subscription, monitor_instance, db_name, pl_table_name, schema_name=pl_schema_name)

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
                    TIMESTAMP_MODELING_ROLE, output_data_schema)

                # Reading the borrowed records
                borrowed_df = self._read_borrowed_data(
                    subscription, db_name, pl_table_name, min_records - rows_analyzed, timestamp_column, last_processed_time, inputs, schema_name=pl_schema_name)

                # Calculating DI variables on borrowed records
                borrowed_di_dict = self.calculate_group_bias(
                    borrowed_df, inputs, data_types, model_type)

                # Merging the DI values
                di_dict = BatchUtils.merge_di_dicts(di_dict, borrowed_di_dict)
            elif rows_analyzed == 0:
                # No new records were read, adding flag to copy the previous measurements, if exists
                self.logger.info("No new records were read, adding the copy measurement flag in output file.")
                copy_measurement = True

            end_time = time.time()
            time_taken = end_time - start_time

            output_json = None
            # Checking if enough records were present
            if min_records is not None:
                rows_analyzed = get(di_dict, "rows_analyzed")
                if rows_analyzed < min_records:
                    self.logger.warning("Not enough records received for group bias computation as rows analyzed {} and min_records {}. Hence, not adding the DI dictionary in output file.".format(rows_analyzed, min_records))
                    # Not enough records present in the PL table
                    output_json = {
                        "job_output": [
                            {
                                "data_name": "payload",
                                "rows_analyzed": rows_analyzed,
                                "time_taken": time_taken
                            }
                        ]
                    }

            if output_json is None:
                # Building the output JSON
                self.logger.info("Adding the DI dictionary computed in the output file.")
                output_json = {
                    "job_output": [
                        {
                            "data_name": "payload",
                            "counts": di_dict,
                            "time_taken": time_taken
                        }
                    ]
                }
            
            # Adding the copy measurement flag for `payload` data
            output_json["job_output"][0]["copy_measurement"] = copy_measurement

            # Converting the value of outermost value as string because of #19045
            output_json["job_output"] = json.dumps(output_json["job_output"])

            # Write to HDFS
            output_file_name = "{}.json".format(self.name)
            output_path = "{}/{}".format(output_file_path, output_file_name)
            self.save_data(path=output_path, data_json=output_json)
            self.logger.info("The output file successfully stored in HDFS at {}.".format(output_path))
        except Exception as ex:
            self.save_exception_trace(str(ex))
            raise ex
        
        return

    def _read_data(self, subscription: dict, monitor_instance: dict, db_name: str, table_name: str, schema_name: str=None):
        """
        Reads and returns data frame for group bias computation.
        :subscription: The subscription object.
        :monitor_instance: The monitor instance object.
        :db_name: The database name.
        :table_name: The table name.
        :schema_name: The name of the schema in which the table resides. [Optional]

        :returns: The data and a flag indicating if records are to be borrowed if required. (from pyspark.sql.dataframe import DataFrame)
        """
        df = None
        borrow_if_needed = False

        # Checking if record timestamp column is present in the PL table
        output_data_schema = get(
            subscription, "entity.asset_properties.output_data_schema")
        timestamp_present = BatchUtils.check_if_modeling_role_present(
            TIMESTAMP_MODELING_ROLE, output_data_schema)
        
        # Getting the record-id column
        record_id_column = BatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        
        # Getting the probability column (Would be None in case of regression models)
        probability_column = BatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

        # Getting all the columns
        columns_to_map = [field["name"] for field in get(output_data_schema, "fields")]
        columns_to_filter = [record_id_column]

        if not timestamp_present:
            # Raise an exception as the timestamp column is mandatory because of #19570
            raise Exception(
                "Mandatory timestamp column is not present in the schema!")

        # Getting the min records
        min_records = get(monitor_instance, "entity.parameters.min_records")

        # Getting the partition information
        payload_data_source = BatchUtils.get_data_source_from_subscription(subscription, "payload")
        partition_column = get(payload_data_source, "parameters.partition_column")
        num_partitions = get(payload_data_source, "parameters.num_partitions")
        if num_partitions is None:
            spark_settings = self.arguments.get("spark_settings", BatchUtils.get_spark_settings_from_subscription(subscription))
            if spark_settings is not None:
                num_partitions = int(spark_settings.get("max_num_executors", 1)) * int(spark_settings.get("executor_cores", 1))
            else:
                num_partitions = 1

        # Reading the data
        if timestamp_present:
            self.logger.info("Timestamp column present in the payload logger table.")
            # Checking the last processed time
            last_processed_time = get(monitor_instance, "entity.parameters.last_processed_ts")
            
            # Getting the timestamp column name
            timestamp_column = BatchUtils.get_name_with_modeling_role(
                TIMESTAMP_MODELING_ROLE, output_data_schema)
            
            if min_records is not None:
                self.logger.info("Min records is given in the monitor instance with value {}.".format(min_records))
                if last_processed_time is not None:
                    # This is not the first run, reading from last processed time
                    self.logger.info("This is not the first run for the subscription.")
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type,
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        record_timestamp_column=timestamp_column,
                        start_time=last_processed_time,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
                    borrow_if_needed = True
                else:
                    self.logger.info("This is the first run for the subscription.")
                    # Reading all the records
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type,
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
            else:
                self.logger.info("Min records is not given in the monitor instance.")
                # The `min_records` is not given
                if last_processed_time is not None:
                    self.logger.info("This is not the first run for the subscription.")
                    # This is not the first run, reading from last processed time
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type,
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        record_timestamp_column=timestamp_column,
                        start_time=last_processed_time,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
                else:
                    self.logger.info("This is the first run for the subscription.")
                    # This is the first run, reading all the records
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type,
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
        # This code would be made reachable once #19570 is implemented
        """
        else:
            self.logger.info("Timestamp column not present in the payload logger table.")
            # ------------
            if min_records is None:
                self.logger.info("Min records is not given in the monitor instance.")
                # When both min records and record-timestamp column is not present
                df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type,
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
            else:
                self.logger.info("Min records is given in the monitor instance without timestamp column, which is not supported.")
                # This case is handled at the configuration level,
                # we throw an error in this case
                pass
            # ------------
        """
        return df, borrow_if_needed

    def _read_borrowed_data(self, subscription: dict, db_name: str, table_name: str, num_records: int, timestamp_column: str, last_processed_time: str, inputs: dict, schema_name: str=None):
        """
        Reads and returns the latest borrowed records older than last processed time.
        :subscription: Yhe subscription object.
        :db_name: The database name.
        :table_name: The table name.
        :num_records: The number of records to be read.
        :timestamp_column: The timestamp column in the table.
        :last_processed_time: The last processed time for fairness.
        :inputs: The inputs dictionary.
        :schema_name: The name of the schema in which the table resides. [Optional]

        :returns: Returns the borrowed records data frame. (from pyspark.sql.dataframe import DataFrame)
        """
        df = None

        self.logger.info("Borrowing records from previous window.")

        # Checking if record timestamp column is present in the PL table
        output_data_schema = get(
            subscription, "entity.asset_properties.output_data_schema")
        timestamp_present = BatchUtils.check_if_modeling_role_present(
            TIMESTAMP_MODELING_ROLE, output_data_schema)
        
        # Getting the record-id column
        record_id_column = BatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        
        # Getting the probability column (Would be None in case of regression models)
        probability_column = BatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

        # Getting all the columns
        columns_to_map = [field["name"] for field in get(output_data_schema, "fields")]
        columns_to_filter = [record_id_column]

        # Getting the partition information
        payload_data_source = BatchUtils.get_data_source_from_subscription(subscription, "payload")
        partition_column = get(payload_data_source, "parameters.partition_column")
        num_partitions = get(payload_data_source, "parameters.num_partitions")
        if num_partitions is None:
            spark_settings = self.arguments.get("spark_settings", BatchUtils.get_spark_settings_from_subscription(subscription))
            if spark_settings is not None:
                num_partitions = int(spark_settings.get("max_num_executors", 1)) * int(spark_settings.get("executor_cores", 1))
            else:
                num_partitions = 1

        # Reading the data
        df = DbUtils.get_table_as_dataframe(
            self.spark,
            self.location_type,
            db_name,
            table_name,
            schema_name=schema_name,
            connection_properties=self.jdbc_connection_properties,
            columns_to_map=columns_to_map,
            columns_to_filter=columns_to_filter,
            record_timestamp_column=timestamp_column,
            end_time=last_processed_time,
            probability_column=probability_column,
            order_by_timestamp_desc=True,
            partition_column=partition_column,
            num_partitions=num_partitions
        )

        # Getting all labels
        all_labels = get(inputs, "favourable_class") + get(inputs, "unfavourable_class")
        label_column = get(inputs, "class_label")

        # Filtering unused label rows
        model_type = get(subscription, "entity.asset.problem_type")
        if model_type == REGRESSION_MODEL_TYPE:
            all_label_query = SQLUtils.get_num_filter_query(label_column, all_labels)
        else:
            all_label_query = SQLUtils.get_cat_filter_query(label_column, "==", all_labels)
        
        # Applying the query
        df = df.filter(all_label_query)

        # Now appying the limit to get the required number of records
        df = df.limit(num_records)

        return df
