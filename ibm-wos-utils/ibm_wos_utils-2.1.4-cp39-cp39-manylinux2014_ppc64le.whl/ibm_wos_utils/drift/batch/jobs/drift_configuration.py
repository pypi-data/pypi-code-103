# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import logging
import tarfile
from io import BytesIO

from ibm_wos_utils.drift.batch.constraints.manager import DataConstraintMgr
from ibm_wos_utils.drift.batch.drift_detection_model import DriftDetectionModel
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORICAL_UNIQUE_THRESHOLD, MAX_DISTINCT_CATEGORIES)
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.hive_utils import get_table_as_dataframe
from ibm_wos_utils.joblib.utils.param_utils import get

logger = logging.getLogger(__name__)


class DriftConfiguration(AIOSBaseJob):

    def __add_json_file(self, name, some_dict):
        some_json = BytesIO(json.dumps(some_dict, indent=4).encode("utf-8"))
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(some_json.getvalue())
        return {
            "tarinfo": tarinfo,
            "fileobj": some_json
        }

    def save_status(self, status: str, additional_info: dict = {}):
        if self.show_progress:
            status_json = {"status": status}
            if len(additional_info):
                status_json.update(additional_info)
            self.save_data(
                self.output_file_path +
                "/drift_config_status.json",
                status_json
            )

    def run_job(self):
        try:
            logger.info(
                "===================== Drift Configuration has been triggered =================")
            self.output_file_path = get(self.arguments, "output_file_path")
            self.show_progress = get(self.arguments, "show_progress", True)

            self.save_status("STARTED")

            self.enable_model_drift = get(
                self.arguments, "enable_model_drift", False)
            self.enable_data_drift = get(
                self.arguments, "enable_data_drift", False)
            logger.info(
                "enable_model_drift:{} and enable_data_drift:{}".format(
                    self.enable_model_drift,
                    self.enable_data_drift))

            # Validate connection parameters
            tables = get(self.arguments, "tables", [])
            training_table = [
                table for table in tables if get(
                    table, "type", "") == "training"]
            if not len(tables) or not len(training_table):
                raise Exception(
                    "The database and/or table for reading training data is missing.")
            training_table = training_table[0]
            database = get(training_table, "database")
            table = get(training_table, "table")

            if not database or not table:
                raise Exception(
                    "The database and/or table for reading training data is missing.")

            self.feature_columns = get(
                self.arguments, "common_configuration.feature_columns", [])
            if not self.feature_columns:
                raise Exception("No feature columns are added.")

            # Validate model type
            self.model_type = get(
                self.arguments,
                "common_configuration.problem_type")
            if (not self.model_type):
                raise Exception("No model type is specified.")
            if self.model_type == "regression" and self.enable_model_drift:
                logger.warning(
                    "The model type specified is regression. Disabling model drift.")
                self.enable_model_drift = False

            columns_to_filter = []
            self.prediction_column = get(
                self.arguments, "common_configuration.prediction")
            if self.model_type != "regression":
                if not self.prediction_column:
                    raise Exception(
                        "The prediction column is missing from arguments.")
                columns_to_filter.append(self.prediction_column)

            self.record_id_column = get(
                self.arguments, "common_configuration.record_id")
            if not self.record_id_column:
                raise Exception(
                    "The record id column is missing from arguments.")

            self.label_column = get(
                self.arguments,
                "common_configuration.label_column")
            if not self.label_column:
                raise Exception("No label column is supplied.")

            columns = self.feature_columns.copy()
            columns.append(self.prediction_column)
            columns.append(self.record_id_column)
            columns.append(self.label_column)

            self.record_timestamp_column = get(
                self.arguments, "common_configuration.record_timestamp")
            if self.record_timestamp_column is not None:
                columns.append(self.record_timestamp_column)

            self.probability_column = get(
                self.arguments, "common_configuration.probability")
            if self.probability_column is not None:
                columns.append(self.probability_column)

            spark_df = get_table_as_dataframe(
                self.spark,
                database,
                table,
                columns,
                columns_to_filter)

            # Validate feature columns
            missing_columns = list(
                set(self.feature_columns) - set(spark_df.columns))
            if len(missing_columns) > 0:
                raise Exception(
                    "The feature columns {} are not present in the training data.".format(missing_columns))
            logger.info("******** Feature Columns [{}]: {} ********".format(
                len(self.feature_columns), self.feature_columns))

            # Validate categorical columns
            self.categorical_columns = get(
                self.arguments, "common_configuration.categorical_columns", [])
            missing_columns = list(
                set(self.categorical_columns) - set(spark_df.columns))
            if len(missing_columns) > 0:
                raise Exception(
                    "The categorical columns {} are not present in the training data.".format(missing_columns))
            logger.info("******** Categorical Columns [{}]: {} ********".format(
                len(self.categorical_columns), self.categorical_columns))

            # Validate label column
            if self.label_column not in spark_df.columns:
                raise Exception(
                    "The label column {} is not present in the training data.".format(
                        self.label_column))

            # Validate probability and prediction columns
            if self.model_type != "regression":
                if self.prediction_column not in spark_df.columns:
                    raise Exception(
                        "The prediction column '{}' is missing from the training data.".format(
                            self.prediction_column))
                if not self.probability_column:
                    raise Exception(
                        "The probability column is missing from arguments.")
                elif self.probability_column not in spark_df.columns:
                    raise Exception(
                        "The probability column '{}' is missing from the training data.".format(
                            self.probability_column))

            if (not self.enable_model_drift) and (not self.enable_data_drift):
                raise Exception(
                    "One of the two drift monitors need to be enabled")

            constraint_set = None
            drift_model = None
            ddm_properties = {}
            if self.enable_model_drift:
                drift_model, ddm_properties = self.run_ddm_job(spark_df)

            if self.enable_data_drift:
                constraint_set = self.run_constraint_generation(spark_df)

            schema = DataConstraintMgr.generate_schema(
                record_id_column=self.record_id_column,
                record_timestamp_column=self.record_timestamp_column,
                model_drift_enabled=self.enable_model_drift,
                data_drift_enabled=self.enable_data_drift,
                constraint_set=constraint_set)

            archive = BytesIO()

            with tarfile.open(fileobj=archive, mode="w:gz") as tar:
                # Add schema json to tar
                tar.addfile(
                    **self.__add_json_file("drifted_transactions_schema.json", schema.to_json()))

                if self.enable_model_drift:
                    model_path = self.output_file_path + "/drift_detection_model"
                    drift_model.save(model_path)
                    ddm_properties["drift_model_path"] = model_path

                    # Add ddm properties to tar
                    tar.addfile(
                        **self.__add_json_file("ddm_properties.json", ddm_properties))

                if self.enable_data_drift:
                    # Add constraints to tar
                    tar.addfile(
                        **self.__add_json_file("data_drift_constraints.json", constraint_set.to_json()))

            # Write the whole tar.gz as a sequence file to HDFS
            self.spark.sparkContext.parallelize([archive.getvalue()]).map(lambda x: (None, x)).coalesce(
                1).saveAsSequenceFile(self.output_file_path + "/drift_configuration")
            archive.close()

            self.save_status("FINISHED")
        except Exception as ex:
            logger.exception(str(ex))
            self.save_exception_trace(str(ex))
            self.save_status("FAILED", additional_info={"exception": str(ex)})
            raise ex
        finally:
            pass

    def run_ddm_job(self, spark_df):
        logger.info("===Drift detection model training process started===")
        self.save_status("Model Drift Configuration STARTED")
        # Get inputs
        ddm_inputs = {
            "model_type": self.model_type,
            "feature_columns": self.feature_columns,
            "categorical_columns": self.categorical_columns,
            "label_column": self.label_column,
            "prediction": self.prediction_column,
            "probability": self.probability_column,
            "enable_tuning": get(
                self.arguments,
                "drift_parameters.model_drift.enable_drift_model_tuning",
                False),
            "max_bins": get(
                self.arguments,
                "drift_parameters.model_drift.max_bins", -1)
        }
        ddm = DriftDetectionModel(
            spark_df, ddm_inputs)
        ddm.generate_drift_detection_model()

        # Save the properties
        ddm_properties = {
            "build_id": ddm.build_id,
            "feature_columns": ddm.feature_columns,
            "categorical_columns": ddm.categorical_columns,
            "class_labels": ddm.class_labels,
            "prediction": ddm.prediction,
            "predicted_labels": ddm.predicted_labels,
            "probability": ddm.probability,
            "ddm_features": ddm.ddm_features,
            "ddm_prediction": ddm.ddm_prediction_col,
            "ddm_probability_difference": ddm.ddm_probability_diff_col,
            "base_model_accuracy": ddm.base_model_accuracy,
            "base_predicted_accuracy": ddm.base_predicted_accuracy
        }

        logger.info("===Drift detection model training process completed===")
        return ddm.ddm_model, ddm_properties

    def run_constraint_generation(self, spark_df):
        logger.info("Constraint generation process has started")
        self.save_status("Data Drift Configuration STARTED")
        logger.info(
            "******* Number of Partitions: {} ********".format(spark_df.rdd.getNumPartitions()))

        drift_options = {
            "enable_two_col_learner": get(
                self.arguments,
                "drift_parameters.data_drift.enable_two_col_learner",
                True),
            "categorical_unique_threshold": get(
                self.arguments,
                "drift_parameters.data_drift.categorical_unique_threshold",
                CATEGORICAL_UNIQUE_THRESHOLD),
            "max_distinct_categories": get(
                self.arguments,
                "drift_parameters.data_drift.max_distinct_categories",
                MAX_DISTINCT_CATEGORIES)}

        constraint_set = DataConstraintMgr.learn_constraints(
            training_data=spark_df,
            feature_columns=self.feature_columns,
            categorical_columns=self.categorical_columns,
            callback=self.save_status,
            **drift_options)

        logger.info("===Constraint generation process has completed===")
        return constraint_set
