# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import collections
import json
import logging
import tarfile

import numpy as np
import pandas as pd

from ibm_wos_utils.drift.batch.constraints.entity import DataConstraintSet
from ibm_wos_utils.drift.batch.constraints.schema import \
    DriftedTransactionsSchema
from ibm_wos_utils.drift.batch.util.constants import (
    DRIFT_RANGE_BUFFER_LOWER_BOUND, DRIFT_RANGE_BUFFER_UPPER_BOUND)

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.hive_utils import get_table_as_dataframe
from ibm_wos_utils.joblib.utils.param_utils import get

try:
    import pyspark.sql.functions as F
    from py4j.protocol import Py4JJavaError
    from pyspark import Row, SparkFiles
    from pyspark.ml import PipelineModel
    from pyspark.sql.types import (BooleanType, DoubleType, StringType,
                                StructField, StructType)
except ImportError as iex:
    pass

logger = logging.getLogger(__name__)


class DriftEvaluation(AIOSBaseJob):

    def run_job(self):
        logger.info("===================== This is drift evaluation job from wos utils package executed by entrypoint job (job/main_job.py) =================")
        logger.debug(self.arguments)

        try:
            self.feature_columns = get(self.arguments, "feature_columns", [])
            self.record_id_column = get(self.arguments, "record_id_column")
            self.record_timestamp_column = get(
                self.arguments, "record_timestamp_column")
            self.columns = self.feature_columns.copy()
            self.columns.append(self.record_id_column)
            if self.record_timestamp_column is not None:
                self.columns.append(self.record_timestamp_column)

            # validate payload table and drift table schemas
            self.__validate_tables_schema()

            # get drift table details
            drift_database, drift_schema, drift_table = self.__get_drift_table()

            # retrieve drift configuration json from hdfs and load constraints
            # and drift model jsons
            constraints_json, schema_json, drift_model, drift_model_properties_json = self.__load_drift_archive()

            # load data constraints
            if self.data_drift_enabled:
                data_constraint_set = DataConstraintSet()
                data_constraint_set.from_json(constraints_json)
            else:
                data_constraint_set = None

            schema = DriftedTransactionsSchema()
            schema.from_json(schema_json)

            if drift_model_properties_json is not None:
                probability = drift_model_properties_json["probability"]
                self.columns.append(probability)

            # get spark dataframe handle to payload table
            payload_spark_df = self.__get_payload_spark_df()

            # transform payload df
            payload_spark_df = self.transform_payload(
                payload_spark_df, drift_model_properties_json)

            # run drift evaluation
            result = self.evaluate(
                payload_spark_df=payload_spark_df, drift_model=drift_model,
                ddm_properties=drift_model_properties_json,
                schema=schema, data_constraint_set=data_constraint_set,
                drift_database=drift_database, drift_table=drift_table)
            logger.info("Evaluation result: {}".format(result))
            logger.debug(type(result))

            output = {
                "metrics": str(result)
            }
            self.save_data(
                self.arguments.get("output_file_path") +
                "/metrics.json",
                data_json=output,
                mode="append")
        except Exception as ex:
            logger.error(str(ex))
            super().save_exception_trace(str(ex))
            raise ex

    def evaluate(
            self,
            payload_spark_df,
            drift_model=None,
            ddm_properties={},
            schema=None,
            data_constraint_set=None,
            drift_database: str = None,
            drift_table: str = None,
            csv_path: str = None):

        if self.record_id_column not in payload_spark_df.columns:
            raise Exception(
                "{} column is not present in payload.".format(
                    self.record_id_column))

        if self.record_timestamp_column and self.record_timestamp_column not in payload_spark_df.columns:
            raise Exception(
                "{} column is not present in payload.".format(
                    self.record_timestamp_column))

        if self.model_drift_enabled and drift_model is None:
            raise Exception("Drift Detection Model is not present.")

        # set run id and initialize violations counter
        self.run_id = get(self.arguments, "monitoring_run_id")

        from ibm_wos_utils.drift.batch.util.dict_accumulator import DictParam
        self.violations_counter = self.sc.accumulator({}, DictParam())

        fields = [
            StructField("constraints_generation_id", StringType(), True),
            StructField("run_id", StringType(), True),
            StructField(self.record_id_column, StringType(), True),
            StructField("is_model_drift", BooleanType(), True),
            StructField("drift_model_confidence", DoubleType(), True),
            StructField("is_data_drift", BooleanType(), True)
        ]

        if self.record_timestamp_column:
            fields.append(
                StructField(
                    self.record_timestamp_column,
                    DoubleType(),
                    True))

        for constraint in schema.bitmap:
            fields.append(StructField(constraint, StringType(), True))

        annotations_schema = StructType(fields=fields)

        ddm_prediction_column = None
        if self.model_drift_enabled:
            ddm_prediction_column = ddm_properties.get(
                "ddm_prediction", "prediction")
            payload_spark_df = drift_model.transform(payload_spark_df)

        columns = list(payload_spark_df.columns)

        drift_evaluation = DriftEval(
            self.run_id,
            schema,
            self.violations_counter,
            columns,
            self.record_id_column,
            self.record_timestamp_column,
            data_constraint_set,
            self.model_drift_enabled,
            self.data_drift_enabled,
            self.feature_columns,
            ddm_prediction_column)

        payload_spark_df = payload_spark_df.rdd.mapPartitionsWithIndex(
            drift_evaluation.partitionFn).toDF(annotations_schema)

        if self.record_timestamp_column:
            payload_spark_df = payload_spark_df.withColumn(
                self.record_timestamp_column, F.from_unixtime(
                    F.col(self.record_timestamp_column)))

        if not drift_database or not drift_table:
            # Only for unit tests
            payload_spark_df.write.mode(
                "overwrite").csv(csv_path, header=True)
        else:
            payload_spark_df.write.mode("append").format("hive").saveAsTable(
                "{}.{}".format(drift_database, drift_table))

        self.__set_drift_magnitudes(ddm_properties)

        counter_str = {
            "total_records": self.total_rows,
            "total_records_current_window": self.total_rows,
            "records_start_time": self.records_start_time,
            "records_end_time": self.records_end_time,
        }
        self.violations_counter.add(counter_str)

        return self.violations_counter.value

    def transform_payload(self, spark_df, drift_model_properties_json=None):
        self.records_start_time = None
        self.records_end_time = None
        if self.record_timestamp_column:
            timestamp_stats = spark_df.select(
                F.min(
                    F.col(
                        self.record_timestamp_column)).alias("min"), F.max(
                    F.col(
                        self.record_timestamp_column)).alias("max")).collect()[0]
            self.records_start_time = timestamp_stats.min.isoformat()
            self.records_end_time = timestamp_stats.max.isoformat()
        logger.info(
            "[SPARKOP] Payload records are between {} and {}.".format(
                self.records_start_time,
                self.records_end_time))
        logger.info("Payload Schema before transformation:")
        logger.info(spark_df.printSchema())

        if self.model_drift_enabled:
            class_labels = drift_model_properties_json["class_labels"]
            probability = drift_model_properties_json["probability"]
            probability_diff_col = drift_model_properties_json["ddm_probability_difference"]
            build_id = drift_model_properties_json["build_id"]

            for idx, _ in enumerate(class_labels):
                prob_col_name = "{}_{}_{}".format(probability, build_id, idx)
                spark_df = spark_df.withColumn(
                    prob_col_name, F.col(
                        probability).getItem(idx))

            max_probability = F.reverse(F.array_sort(
                F.col(probability))).getItem(0)
            second_probability = F.reverse(
                F.array_sort(F.col(probability))).getItem(1)
            spark_df = spark_df.withColumn(
                probability_diff_col,
                max_probability - second_probability)

            spark_df = spark_df.drop(probability)

        logger.info("Payload Schema after transformation:")
        logger.info(spark_df.printSchema())
        return spark_df

    def __set_drift_magnitudes(self, drift_model_properties_json):
        counter_str = {}

        if self.model_drift_enabled:
            model_drifted_count = get(
                self.violations_counter.value, "model_drift.count", 0)
            base_client_accuracy = get(
                drift_model_properties_json,
                "base_model_accuracy")
            base_predicted_accuracy = get(
                drift_model_properties_json,
                "base_predicted_accuracy")

            accuracy = (self.total_rows - model_drifted_count) / \
                self.total_rows

            predicted_accuracy = accuracy + \
                (base_client_accuracy - base_predicted_accuracy)

            # add -0.07 to the predicted accuracy to get min of predicted accuracy range
            # add +0.02 to the predicted accuracy to get max of predicted
            # accuracy range
            predicted_accuracy_range = [
                predicted_accuracy +
                DRIFT_RANGE_BUFFER_LOWER_BOUND,
                predicted_accuracy +
                DRIFT_RANGE_BUFFER_UPPER_BOUND]
            # predicted_accuracy is the midpoint of the above range, with 1.0
            # as the cap.
            predicted_accuracy = min(1.0, sum(predicted_accuracy_range) / 2)

            if predicted_accuracy < accuracy:
                predicted_accuracy = accuracy

            # drift magnitude is just the difference between base client
            # (train) accuracy and predicted accuracy
            drift_magnitude = base_client_accuracy - predicted_accuracy
            drift_magnitude = max(0, drift_magnitude)
            counter_str.update({
                "model_drift": {
                    "magnitude": drift_magnitude,
                    "predicted_accuracy": predicted_accuracy
                }
            })

        if self.data_drift_enabled:
            data_drifted_count = get(
                self.violations_counter.value, "data_drift.count", 0)
            data_drift_magnitude = data_drifted_count / self.total_rows
            counter_str.update({
                "data_drift": {
                    "magnitude": data_drift_magnitude
                }
            })

        logger.info(
            "Adding drift magnitude and predicted accuracy to counter. {}".format(counter_str))
        self.violations_counter.add(counter_str)
        return

    def __validate_tables_schema(self):
        is_error = False
        error_json = {
            "error": []
        }

        tables_to_be_validated = get(self.arguments, "tables", [])

        # Set map_data_types property to True if not present in the payload
        map_data_types = get(self.arguments, "map_data_types")
        if map_data_types is not None:
            if not map_data_types or map_data_types.lower() == "false":
                map_data_types = False
            else:
                map_data_types = True
        else:
            map_data_types = True

        for table in tables_to_be_validated:
            table_name = get(table, "table")
            database_name = get(table, "database")
            logger.info(
                "Retrieving columns of table {}:{}".format(
                    database_name, table_name))
            columns = self.spark.catalog.listColumns(
                tableName=table_name, dbName=database_name)
            actual_schema = {}

            # Mapping between Hive and Spark data types. Datatypes like 'map', 'array' which are present in both
            # Hive and Spark are not part of the mapping below. Hive data type is used in that case.
            # Reference:
            # https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/integrating-hive/content/hive_hivewarehouseconnector_supported_types.html
            hive_to_spark_map = {
                "tinyint": "byte",
                "smallint": "short",
                "integer": "integer",
                "int": "integer",
                "bigint": "long",
                "float": "float",
                "double": "double",
                "decimal": "decimal",
                "string": "string",
                "varchar": "string",
                "binary": "binary",
                "boolean": "boolean",
                "interval": "calendarinterval"
            }

            for column in columns:
                if map_data_types:
                    data_type = get(hive_to_spark_map, column.dataType.lower())
                    if data_type is None:
                        data_type = column.dataType.lower()

                        # For hive datatype of format like: array<int>, fetch the inner datatype and convert it
                        # Complex datatypes like array, map are present in both
                        # hive and spark
                        type_split = data_type.split("<")
                        if len(type_split) > 1:
                            type_split_0 = type_split[0]
                            type_split_1 = type_split[1][:-1]
                            spark_sub_type = get(
                                hive_to_spark_map, type_split_1)
                            if spark_sub_type is not None:
                                data_type = "{}<{}>".format(
                                    type_split_0, spark_sub_type)

                    actual_schema[column.name.lower()] = data_type
                else:
                    actual_schema[column.name.lower(
                    )] = column.dataType.lower()

            # validate table schema
            # iterate through expected column names and verify they exist in target table
            # we are verifying expected list, its okay for target table to have
            # a lot more columns than expectation
            logger.info("Validating schema...")
            expected_columns = get(table, "columns")
            logger.info("Expected columns : {}".format(expected_columns))
            logger.info("Actual Schema: {}".format(actual_schema))
            for column in get(expected_columns, "fields"):
                if get(column, "metadata.deleted") is True:
                    # skip validation if this column has metadata with deleted
                    # set to true
                    continue

                key = get(column, "name")
                value = get(column, "type")

                # column name validation
                if not key or key.lower() not in actual_schema.keys():
                    is_error = True
                    error_json["error"].append({
                        "database": database_name,
                        "table": table_name,
                        "error": "Column '{}' not found in {} table.".format(key, table_name)
                    })
                    continue

                if value is None:
                    # Unlikely to happen
                    is_error = True
                    error_json["error"].append({
                        "database": get(table, "database"),
                        "table": get(table, "table"),
                        "error": "No expected value present for column {}.".format(key)
                    })
                    continue

                valid_values = []
                integrals = ["short", "integer", "long"]
                fractions = ["float", "double", "decimal"]

                if isinstance(value, collections.Mapping):
                    # for columns with the type stored in a dictionary, prepare
                    # column type as a string
                    data_type = value.get("type").lower()
                    element_type = value.get("elementType").lower()
                    if element_type.lower() in integrals:
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), integrals))
                    elif element_type.lower() in fractions:
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), fractions))
                    else:
                        valid_values = [
                            "{}<{}>".format(
                                data_type, element_type)]
                elif value.lower() in integrals:
                    valid_values = integrals
                elif value.lower() in fractions:
                    valid_values = fractions
                else:
                    valid_values = [value.lower()]

                # column name found, validate column datatype
                if str(actual_schema[key.lower()]) not in valid_values:
                    is_error = True
                    error_json["error"].append({
                        "database": get(table, "database"),
                        "table": get(table, "table"),
                        "error": "Datatype mismatch for column {}: expected '{}', actual '{}'.".format(
                            key, valid_values, actual_schema[key.lower()])
                    })

        if is_error:
            raise Exception(
                "Table(s) validation failed : {}.".format(error_json))
        logger.info("Table schema successfully validated!")

    def __load_drift_archive(self):
        # get data drift enabled flag
        self.data_drift_enabled = get(
            self.arguments, "data_drift.enabled")
        self.data_drift_enabled = False if self.data_drift_enabled in [
            "False", "false", False] else True

        # get model drift enabled flag
        self.model_drift_enabled = get(
            self.arguments, "model_drift.enabled")
        self.model_drift_enabled = False if self.model_drift_enabled in [
            "False", "false", False] else True

        constraints_json = None
        schema_json = None
        drift_model_properties_json = None
        drift_model = None
        self.sc.addFile(self.arguments.get("data_file_path") + "/drift.tar.gz")
        with tarfile.open(SparkFiles.get("drift.tar.gz")) as drift_archive_handle:
            schema_json = json.load(
                drift_archive_handle.extractfile("drifted_transactions_schema.json"))
            if self.data_drift_enabled:
                constraints_json = json.load(
                    drift_archive_handle.extractfile("data_drift_constraints.json"))

            if self.model_drift_enabled:
                drift_model_properties_json = json.load(
                    drift_archive_handle.extractfile("ddm_properties.json"))
                try:
                    drift_model = PipelineModel.load(
                        drift_model_properties_json["drift_model_path"])
                except Py4JJavaError as ex:
                    logger.exception(ex)

                    # Handle case where Drift Model was not found in HDFS
                    if "Input path does not exist" in str(ex):
                        new_ex = Exception(
                            "Drift Detection Model was not found at {}".format(
                                drift_model_properties_json["drift_model_path"]))
                        logger.exception(new_ex)
                        self.save_exception_trace(str(new_ex))
                        raise new_ex

                    # Throw back the original error for everything else
                    self.save_exception_trace(str(ex))
                    raise ex

        logger.debug("Constraints Json: {}".format(constraints_json))
        logger.debug("Schema Json: {}".format(schema_json))
        logger.debug("Drift Model: {}".format(True if drift_model else False))
        logger.debug("Drift Model Properties Json: {}".format(
            drift_model_properties_json))

        return constraints_json, schema_json, drift_model, drift_model_properties_json

    def __get_payload_spark_df(self):
        storage_type = get(self.arguments, "storage.type")

        if storage_type != "hive":
            raise Exception(
                "Unsupported storage type '{}'.".format(storage_type))

        payload_database, _, payload_table = self.__get_payload_table()

        start_time = get(self.arguments, "start_time")
        end_time = get(self.arguments, "end_time")

        # optional stuff, we may or may not have these in input
        min_samples = get(self.arguments, "min_samples")
        record_timestamp_column = get(
            self.arguments, "record_timestamp_column")

        """
        Following scenarios are possible:
        => min_samples = None, record_timestamp_column = None
            In this case, we analyze entire table.

        => min_samples = None, record_timestamp_column != None
            In this case, we analyze all the records between start_time and end_time.
            Its possible, we find no records in this time window. In such case, drift
            will throw an error.

        => min_samples != None, record_timestamp_column = None
            In this case, if the total records in table are less than min_samples,
            we throw an error. Otherwise, we analyze entire table.
            TODO: In latter case, should we limit analysis to min_samples size ?

        => min_samples != None, record_timestamp_column != None
            In this case, if the record count between start_time and end_time is less than
            min_samples, we throw exception with error minimum records not found.
            Otherwise, we analyze all the records between start_time and end_time.
        """
        spark_df = get_table_as_dataframe(
            spark=self.spark,
            database_name=payload_database,
            table_name=payload_table,
            columns_to_map=self.columns,
            columns_to_filter=[self.record_id_column],
            record_timestamp_column=record_timestamp_column,
            start_time=start_time,
            end_time=end_time)

        self.total_rows = spark_df.count()
        logger.info(
            "[SPARKOP] Total {} rows in payload".format(
                self.total_rows))
        
        empty_df = (self.total_rows == 0)
        insufficient_df = (min_samples and (self.total_rows < min_samples))

        if empty_df or insufficient_df:
            error_message = "The payload table {} has {} rows".format(
                payload_table, self.total_rows)
            if record_timestamp_column and (start_time and not end_time):
                error_message += " after {}".format(start_time)
            elif record_timestamp_column and (not start_time and end_time):
                error_message += " before {}".format(end_time)
            elif record_timestamp_column and (start_time and end_time):
                error_message += " between {} and {}".format(
                    start_time, end_time)

            if insufficient_df:
                error_message += ". The minimum number required for evaluation: {} rows.".format(
                    min_samples)

            raise Exception(error_message)

        return spark_df

    def __get_payload_table(self):
        return self.__get_table(table_type="payload")

    def __get_drift_table(self):
        return self.__get_table(table_type="drift")

    def __get_table(self, table_type: str, is_schema_required: bool = False):
        tables = get(self.arguments, "tables", [])
        # get table details
        table_details = [
            table for table in tables if get(
                table, "type", "") == table_type]
        if not len(table_details):
            raise Exception(
                "Table details of type {} are missing".format(table_type))

        database = get(table_details[0], "database")
        schema = get(table_details[0], "schema")
        table = get(table_details[0], "table")

        if not database or not table:
            raise Exception(
                "The database and/or table for table type {} is missing.".format(table_type))

        if is_schema_required and not schema:
            raise Exception(
                "Schema for table type {} is missing.".format(table_type))

        return database, schema, table


class DriftEval(object):
    # TODO This CHUNK_SIZE needs to be computed based on the cluster
    CHUNK_SIZE = 10000

    def __init__(
            self,
            run_id: str,
            schema,
            violations_counter,
            columns,
            record_id_column,
            record_timestamp_column=None,
            data_constraint_set=None,
            model_drift_enabled=False,
            data_drift_enabled=False,
            feature_columns=[],
            ddm_prediction_column=None):
        self.schema = schema
        self.run_id = run_id
        self.violations_counter = violations_counter
        self.columns = columns
        self.record_id_column = record_id_column
        self.record_timestamp_column = record_timestamp_column
        self.model_drift_enabled = model_drift_enabled
        self.data_drift_enabled = data_drift_enabled
        self.data_constraint_set = data_constraint_set
        self.feature_columns = feature_columns
        self.ddm_prediction_column = ddm_prediction_column

    def get_annotations(self, violations_df):
        annotations_df = pd.DataFrame()
        annotations_df[self.record_id_column] = violations_df[self.record_id_column].copy()
        if self.record_timestamp_column:
            # Need to convert pandas Timestamp to Unix epoch seconds format. For
            # easier conversion in Spark.
            annotations_df[self.record_timestamp_column] = violations_df[self.record_timestamp_column].apply(
                lambda row: row.timestamp())
        annotations_df["run_id"] = self.run_id
        annotations_df["constraints_generation_id"] = self.schema.id

        if self.model_drift_enabled:
            annotations_df["is_model_drift"] = violations_df["is_model_drift"].copy()
            annotations_df["drift_model_confidence"] = violations_df["drift_model_confidence"]
        else:
            # Need to mark is_model_drift False as BooleanType gives error on
            # Nulls
            annotations_df["is_model_drift"] = False
            annotations_df["drift_model_confidence"] = np.NaN

        if self.data_drift_enabled:
            annotations_df["is_data_drift"] = violations_df["is_data_drift"].copy()
            for column in self.schema.bitmap:
                if len(self.schema.bitmap[column]) > 0:
                    annotations_df[column] = violations_df[self.schema.bitmap[column]].apply(
                        lambda row: "".join(map(str, row)), axis=1)
                else:
                    # For any type of constraint that is not learnt.
                    annotations_df[column] = np.NaN
        else:
            # Need to mark is_data_drift False as BooleanType gives error on
            # Nulls
            annotations_df["is_data_drift"] = False
            for column in self.schema.bitmap:
                annotations_df[column] = np.NaN

        return annotations_df

    def partitionFn(self, index, data):
        import pandas as pd
        from ibm_wos_utils.drift.batch.constraints.manager import \
            DataConstraintMgr
        from more_itertools import ichunked

        chunks = ichunked(data, DriftEval.CHUNK_SIZE)
        for chunk in chunks:
            payload_df = pd.DataFrame(chunk, columns=self.columns)
            violations_df = pd.DataFrame()
            conditions = pd.Series([False] * len(payload_df))

            if self.data_drift_enabled:
                violations_df = DataConstraintMgr.check_violations(
                    index,
                    self.data_constraint_set,
                    payload_df,
                    self.violations_counter,
                    self.record_id_column,
                    self.record_timestamp_column,
                    self.feature_columns)
                constraint_columns = list(
                    self.data_constraint_set.constraints.keys())
                violations_df["is_data_drift"] = violations_df[constraint_columns].sum(
                    axis=1) > 0
                conditions = conditions | violations_df["is_data_drift"]
            else:
                violations_df[self.record_id_column] = payload_df[self.record_id_column].copy(
                )
                if self.record_timestamp_column:
                    violations_df[self.record_timestamp_column] = payload_df[self.record_timestamp_column].copy(
                    )

            if self.model_drift_enabled:
                # If prediction is 0/False, it means there is model drift
                violations_df["is_model_drift"] = ~payload_df[self.ddm_prediction_column].astype(
                    bool)

                # Choose the maximum of probabilities for drift model
                # confidence
                violations_df["drift_model_confidence"] = payload_df["probability"].apply(
                    max)

                # Set drift model confidence as null when is_model_drift is
                # False
                violations_df.loc[violations_df["is_model_drift"]
                                  == False, "drift_model_confidence"] = np.nan
                conditions = conditions | violations_df["is_model_drift"]

                # Get discretized counts for drift confidence intervals between [0.5, 0.55).. so on
                # Last interval is [1.0, 1.05) which only has count of transactions predicted with
                # 100% probability
                boundaries = np.arange(0.5, 1.06, 0.05)
                discretized_counts = pd.cut(violations_df["drift_model_confidence"], boundaries, labels=np.round(
                    boundaries[:-1], 2), include_lowest=True)
                discretized_counts = discretized_counts.value_counts().sort_index().to_dict()

                counter_str = {
                    "model_drift": {
                        "count": sum(violations_df["is_model_drift"]),
                        "bins": discretized_counts
                    }
                }
                logger.warn(
                    "\npart_{} {}".format(
                        str(index).zfill(5),
                        counter_str))
                self.violations_counter.add(counter_str)

            if self.model_drift_enabled and self.data_drift_enabled:
                counter_str = {
                    "model_data_drift": {
                        "count": sum(
                            violations_df["is_model_drift"] & violations_df["is_data_drift"])}}
                logger.warn(
                    "\npart_{} {}".format(
                        str(index).zfill(5),
                        counter_str))
                self.violations_counter.add(counter_str)

            violations_df = violations_df[conditions]
            annotations_df = self.get_annotations(violations_df)

            annotations_df = annotations_df.apply(
                lambda row: Row(**row.to_dict()), axis=1)

            for _, element in annotations_df.iteritems():
                yield element
