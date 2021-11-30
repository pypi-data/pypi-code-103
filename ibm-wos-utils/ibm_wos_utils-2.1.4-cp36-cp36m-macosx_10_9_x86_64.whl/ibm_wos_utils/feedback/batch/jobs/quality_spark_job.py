
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
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

            spark_df, records_count = DataReader(self.logger).read_data(self.spark, scoring_id_col, label_col, prediction_col,
                                        connection_props,timestamp_col, last_updated_timestamp, min_sample_records)
            quality_metrics = MetricsUtils(self.logger).compute_quality_metrics(
                self.sc, spark_df, model_type, label_col, prediction_col, probability_col, records_count)

            output_path = "{}/{}.{}".format(hdfs_path, constants.JOB_OUTPUT_FILE_NAME, constants.JOB_OUTPUT_FILE_FORMAT )
            self.logger.info("Saving the output to the hdfs location: {}".format(output_path))
            self.save_data(output_path, quality_metrics)

            end_time = time.time()
            self.logger.info("Time to complete the  quality spark metrics {}".format(
                end_time-start_time))
        except Exception as ex:
            self.logger.error("Exception while generating  the quality metrics:{0}".format(str(ex)))
            super().save_exception_trace(str(ex))
            raise ex
        #finally:
        #    if self.spark is not None:
        #        self.spark.stop()
        