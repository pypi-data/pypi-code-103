# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import tarfile
import json
import time

try:
    from pyspark import SparkFiles
except ImportError as e:
    pass

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.explainability.batch.utils.compute_explanation import ComputeExplanation
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.explainability.entity.explain_config import ExplainConfig
from ibm_wos_utils.explainability.batch.entity.subscription import Subscription
from ibm_wos_utils.explainability.utils.date_time_util import DateTimeUtil
from ibm_wos_utils.explainability.batch.utils.explanations_store import ExplanationsStore
try:
    from ibm_wos_utils.common.batch.utils.dict_accumulator import DictAccumulator
except NameError:
    pass


class ExplanationsComputation(AIOSBaseJob):

    def run_job(self):
        try:
            # Initialize attributes
            config, score_response = self.get_job_data()
            explain_config = self.get_explain_config(
                config.get("explainability_configuration"))
            self.logger.info(
                "Explainability configuration is " + str(vars(explain_config)))
            subscription = Subscription(config.get("subscription"))
            self.logger.info("Subscription details are " + str(subscription))
            data_source = config["subscription"]["explain_data_source"].copy()
            data_source["jdbc_connection_properties"] = self.jdbc_connection_properties

            self.logger.info("Starting explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))

            # Read payload data
            payload_df = self.__get_payload_df(explain_config, subscription)
            start_time = DateTimeUtil.get_current_datetime()

            # Compute explanation and store response
            explanations_counter = self.sc.accumulator(
                {"failed": 0, "total": 0, "failed_scoring_ids": []}, DictAccumulator())
            payload_empty = payload_df.rdd.isEmpty()
            if payload_empty:
                self.logger.info(
                    "The payload records are empty. Hence skipping the run.")
            else:
                self.logger.info(
                    "The no of partitions in the dataframe are {}".format(payload_df.rdd.getNumPartitions()))
                score_response_bc = self.sc.broadcast(score_response)
                compute_explanation = ComputeExplanation(
                    explain_config=explain_config, subscription=subscription, score_response=score_response_bc, explanations_counter=explanations_counter, created_by=self.arguments.get("created_by"))
                explanations = payload_df.rdd.mapPartitions(
                    compute_explanation.compute)
                store = ExplanationsStore(
                    spark=self.spark, data_source=data_source, logger=self.logger)
                store.store_explanations(explanations)

            self.logger.info("Completed explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))

            explanations_count = explanations_counter.value
            self.logger.info(
                "Explanations count {}".format(explanations_count))
            del explanations_count["failed_scoring_ids"]
            self.__save_explanations(
                data_source=data_source, start_time=start_time,
                end_time=DateTimeUtil.get_current_datetime(), payload_empty=payload_empty, explanations_count=explanations_count)
        except Exception as ex:
            self.logger.error(
                "An error occurred while running the explanations_computation job. " + str(ex))
            super().save_exception_trace(error_msg=str(ex))
            raise ex

    def finish_job(self):
        file_path = self.arguments.get(
            "data_file_path") + "/explain_job_data.tar.gz"
        JoblibUtils.delete_file_from_hdfs(self.spark, file_path)
        super().finish_job()

    def __get_payload_df(self, explain_config, subscription):

        num_partitions = subscription.queue_num_partitions
        if not num_partitions:
            spark_settings = self.arguments.get("spark_settings")
            if spark_settings:
                num_partitions = int(spark_settings.get(
                    "max_num_executors")) * int(spark_settings.get("executor_cores"))
            else:
                num_partitions = 1

        payload_df = DbUtils.get_table_as_dataframe(spark=self.spark,
                                                    database_name=subscription.explanations_db_name,
                                                    schema_name=subscription.explanations_db_schema,
                                                    location_type=subscription.explanations_db_location_type,
                                                    table_name=subscription.queue_table, columns_to_map=self.__get_columns(
                                                        explain_config, subscription),
                                                    columns_to_filter=[
                                                        subscription.scoring_id_column],
                                                    record_timestamp_column=subscription.scoring_timestamp_column,
                                                    start_time=self.arguments.get(
                                                        "records_start_time"),
                                                    end_time=self.arguments.get(
                                                        "records_end_time"),
                                                    connection_properties=self.jdbc_connection_properties,
                                                    probability_column=explain_config.probability_column,
                                                    partition_column=subscription.queue_partition_column,
                                                    num_partitions=num_partitions)

        return payload_df

    def __get_columns(self, explain_config, subscription):
        columns = explain_config.feature_columns.copy()
        if explain_config.prediction_column:
            columns.append(explain_config.prediction_column)
        if explain_config.probability_column:
            columns.append(explain_config.probability_column)
        if subscription.scoring_timestamp_column:
            columns.append(subscription.scoring_timestamp_column)
        columns.append(subscription.scoring_id_column)
        return columns

    def get_explain_config(self, config):

        return ExplainConfig(input_data_type=config.get("input_data_type"),
                             problem_type=config.get("problem_type"),
                             feature_columns=config.get("feature_columns"),
                             categorical_columns=config.get(
                                 "categorical_columns"),
                             prediction_column=config.get("prediction_column"),
                             probability_column=config.get(
                                 "probability_column"),
                             training_stats=config.get("training_statistics"),
                             schema=config.get("features_schema"),
                             features_count=config.get("features_count"),
                             perturbations_count=config.get(
                                 "perturbations_count"),
                             sample_around_instance=config.get(
                                 "sample_around_instance"),
                             discretize_continuous=config.get(
                                 "discretize_continuous"),
                             discretizer=config.get("discretizer"),
                             kernel_width=config.get("kernel_width"),
                             feature_selection=config.get("feature_selection"))

    def get_job_data(self):
        self.sc.addFile(self.arguments.get(
            "data_file_path") + "/explain_job_data.tar.gz")
        with tarfile.open(SparkFiles.get("explain_job_data.tar.gz")) as f:
            config = json.loads(f.extractfile("explain_config.json").read())
            perturbations_score_response = json.loads(
                f.extractfile("explain_scoring_response.json").read())

        return config, perturbations_score_response

    def __save_explanations(self, data_source, start_time, end_time, payload_empty, explanations_count):
        self.logger.info(
            "Getting latest explanations from the run to store in datamart.")

        if payload_empty:
            response = {}
        else:
            store = ExplanationsStore(
                spark=self.spark, data_source=data_source, logger=self.logger)
            search_filters = self.arguments.get("search_filters")
            search_filters = "{},finished_at:ge:{},finished_at:le:{}".format(
                search_filters, DateTimeUtil.get_datetime_db_format(start_time), DateTimeUtil.get_datetime_db_format(end_time))
            response = store.get_explanations(limit=self.arguments.get("limit"),
                                              search_filters=search_filters,
                                              order_by_column=self.arguments.get("order_by_column"))

            # Retry fetching the explanations if not successful
            count = 0
            while explanations_count.get("total") > 0 and not response.get("values") and count < 50:
                self.logger.info(
                    "Could not get explanations from the database to store in datamart. Response {}. Retrying count {}".format(response, count))
                time.sleep(5)
                response = store.get_explanations(limit=self.arguments.get("limit"),
                                                  search_filters=search_filters,
                                                  order_by_column=self.arguments.get("order_by_column"))
                count = count + 1

            if explanations_count.get("total") > 0 and not response.get("values"):
                self.logger.info(
                    "Getting explanations without ordering ...".format(response, count))
                response = store.get_explanations(limit=self.arguments.get("limit"),
                                                  search_filters=search_filters)

        response["explanations_count"] = explanations_count

        self.save_data(self.arguments.get(
            "output_file_path")+"/explanations.json", response)
        self.logger.info(
            "Completed getting latest explanations to store in datamart.")
