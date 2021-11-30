
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import time
import sys
from ibm_wos_utils.feedback.batch.utils.data_reader import DataReader
from ibm_wos_utils.feedback.batch.utils.metrics_utils import MetricsUtils
from ibm_wos_utils.feedback.batch.utils import constants
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob


class QualityJob(AIOSBaseJob):

    def run_job(self):
        """
        CLI Arguments:
            model_type - Type of the deployed model
            label_col - Label column name
            prediction_col - Prediction column name
            probability_col - Prediction column name
            timestamp_col - timestamp column name
            last_updated_timestamp - last run updated timestamp
            min_sample_records - minimum sample records to consider for the job execution
            storage_type - Database storage type
            storage_url =  Database storage url 
            table_name =  Table name in the database
            db_name =  Name of the database

        """
        try:
            start_time = time.time()
            params = self.arguments
            model_type = params.get("model_type")
            label_col = params.get("label_col")
            prediction_col = params.get("prediction_col")
            probability_col = params.get("probability_col")
            scoring_id_col = params.get("scoring_id_col")
            timestamp_col = None
            last_updated_timestamp = None
            if 'timestamp_col' in params:
                timestamp_col = params.get("timestamp_col")
            if 'last_updated_timestamp' in params:
                last_updated_timestamp = params.get("last_updated_timestamp")
            min_sample_records = params.get("min_sample_records")
            connection_props = params.get("storage")
            hdfs_path = params.get("output_file_path")
            spark_settings= params.get("spark_settings")
            output_path = "{}/{}.{}".format(
                hdfs_path, constants.JOB_OUTPUT_FILE_NAME, constants.JOB_OUTPUT_FILE_FORMAT)

            spark_df, counts = DataReader(self.logger).read_data(
                self.spark, scoring_id_col, label_col, prediction_col,
                connection_props, spark_settings, timestamp_col, last_updated_timestamp,
                min_sample_records, probability_column=probability_col)

            quality_metrics = MetricsUtils(self.logger).compute_quality_metrics(
                self.sc, spark_df, model_type, label_col, prediction_col, probability_col, counts)

            self.logger.info(
                "Saving the output to the hdfs location: {}".format(output_path))
            self.save_data(output_path, quality_metrics)

            end_time = time.time()
            self.logger.info("Time to complete the  quality spark metrics {}".format(
                end_time-start_time))
        except Exception as ex:
            exc_message = str(ex)
            if constants.COPY_METRICS_MESSAGE in exc_message:
                metrics_copy_msg = dict()
                metrics_copy_msg["copy_metrics"] = "true"
                self.logger.info(
                    "Saving the copy metrics output to the hdfs location: {}".format(output_path))
                self.save_data(output_path, metrics_copy_msg)
            else:
                if 'error_code' in exc_message:
                    error_code = None
                    error_params = None
                    error_msg = None
                    (args_dict,) = ex.args
                    if args_dict and isinstance(args_dict, dict):
                        error_msg = args_dict.get("error_msg")
                        error_code = args_dict.get("error_code")
                        error_params = args_dict.get("parameters")

                    self.logger.error(error_msg)
                    super().save_exception(error_msg=error_msg,
                        error_code=error_code,
                        parameters=error_params
                    )
                else:
                    self.logger.error(exc_message)
                    super().save_exception_trace(exc_message)
                raise ex
