# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import tarfile
try:
    from pyspark import SparkFiles
except ImportError as e:
    pass

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.explainability.batch.utils.compute_explanation import ComputeExplanation
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.hive_utils import get_table_as_dataframe
from ibm_wos_utils.explainability.entity.explain_config import ExplainConfig
from ibm_wos_utils.explainability.batch.entity.subscription import Subscription
from ibm_wos_utils.explainability.batch.utils.explanations_store import ExplanationsStore


class AdhocExplanationsComputation(AIOSBaseJob):

    def run_job(self):
        scoring_ids = []
        explanation_task_ids = []
        try:
            # Initialize attributes
            config, score_response = self.get_job_data()
            explain_config = self.get_explain_config(
                config.get("explainability_configuration"))
            self.logger.info(
                "Explainability configuration is " + str(vars(explain_config)))
            subscription = Subscription(config.get("subscription"))
            self.logger.info("Subscription details are " + str(subscription))
            scoring_ids = self.arguments.get("scoring_ids")
            explanation_task_ids = self.arguments.get("explanation_task_ids")
            data_source = config["subscription"]["explain_data_source"].copy()
            data_source["jdbc_connection_properties"] = self.jdbc_connection_properties

            payload_df = self.get_payload_df(
                explain_config=explain_config, subscription=subscription)

            rows, missing_rows = self.get_input_rows(
                scoring_ids, explanation_task_ids, payload_df, subscription)

            self.logger.info("Starting adhoc explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))

            score_response_bc = self.sc.broadcast(score_response)
            compute_explanation = ComputeExplanation(
                explain_config=explain_config, subscription=subscription, score_response=score_response_bc, created_by=self.arguments.get("created_by"))

            store = ExplanationsStore(
                spark=self.spark, data_source=data_source, logger=self.logger)
            if rows:
                explanations = self.sc.parallelize(rows).mapPartitions(
                    compute_explanation.compute)
                store.store_explanations(explanations)

            if missing_rows:
                explanations = self.sc.parallelize(
                    missing_rows).mapPartitions(compute_explanation.compute_no_record_explanation)
                store.store_explanations(explanations)

            self.logger.info("Completed adhoc explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))
            self.__save_explanations(
                store, subscription.subscription_id, explanation_task_ids)
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

    def get_input_rows(self, scoring_ids, explanation_task_ids, payload_df, subscription):
        rows = []
        missing_rows = []
        for (scoring_id, task_id) in zip(scoring_ids, explanation_task_ids):
            row = payload_df.filter(
                payload_df[subscription.scoring_id_column] == scoring_id).take(1)
            if row:
                row = row[0].asDict()
                row["explanation_task_id"] = task_id
                rows.append(row)
            else:
                missing_rows.append({
                    subscription.scoring_id_column: scoring_id,
                    "explanation_task_id": task_id
                })
        self.logger.info("Input rows found: " + str(rows))
        self.logger.info("Missing input rows: " + str(missing_rows))
        return rows, missing_rows

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
        print(self.arguments.get("data_file_path"))
        self.sc.addFile(self.arguments.get(
            "data_file_path") + "/explain_job_data.tar.gz")
        with tarfile.open(SparkFiles.get("explain_job_data.tar.gz")) as f:
            config = json.loads(f.extractfile("explain_config.json").read())
            perturbations_score_response = json.loads(
                f.extractfile("explain_scoring_response.json").read())

        return config, perturbations_score_response

    def get_payload_df(self, explain_config, subscription):
        scoring_ids = self.arguments.get("scoring_ids")

        # Read data from explanations queue table
        queue_table_rows = self.__get_payload(connection=subscription.explanations_db_conn,
                                              database=subscription.explanations_db_name,
                                              schema=subscription.explanations_db_schema,
                                              table=subscription.queue_table,
                                              explain_config=explain_config,
                                              subscription=subscription,
                                              scoring_ids=scoring_ids)

        missing_scoring_ids = []
        for s in scoring_ids:
            if queue_table_rows.filter(queue_table_rows[subscription.scoring_id_column] == s).count() < 1:
                missing_scoring_ids.append(s)

        payload_table_rows = None
        if missing_scoring_ids and subscription.payload_db_conn and subscription.payload_table:
            self.logger.info(
                "Could not find scoring ids {} in explanation queue table. Searching in payload table.".format(missing_scoring_ids))

            # Read data from payload table
            payload_table_rows = self.__get_payload(connection=subscription.payload_db_conn,
                                                    database=subscription.payload_db_name,
                                                    schema=subscription.payload_db_schema,
                                                    table=subscription.payload_table,
                                                    explain_config=explain_config,
                                                    subscription=subscription,
                                                    scoring_ids=missing_scoring_ids)

        payload_df = queue_table_rows
        if payload_table_rows:
            payload_df = payload_df.union(payload_table_rows)

        return payload_df

    def __get_payload(self, connection, database, schema, table, explain_config, subscription, scoring_ids):
        location_type = connection.get("location_type")
        if location_type == "jdbc":
            # Read data from explanation queue table in db2
            search_query = "select * from \"{}\".\"{}\" where \"{}\" in ({})".format(
                schema, table, subscription.scoring_id_column, ",".join(["'{}'".format(i) for i in scoring_ids]))
            self.logger.info(
                "Getting payload data using query: {}".format(search_query))
            queue_table_rows = DbUtils.get_table_as_dataframe(spark=self.spark,
                                                              database_name=database,
                                                              schema_name=schema,
                                                              connection_properties=self.jdbc_connection_properties,
                                                              location_type=location_type,
                                                              table_name=table, columns_to_map=self.__get_columns(
                                                                  explain_config, subscription),
                                                              sql_query=search_query,
                                                              probability_column=explain_config.probability_column)
        else:
            # Read data from explanation queue table in hive
            queue_table_rows = get_table_as_dataframe(spark=self.spark,
                                                      database_name=database,
                                                      table_name=table, columns_to_map=self.__get_columns(
                                                          explain_config, subscription),
                                                      columns_to_filter=[
                                                          subscription.scoring_id_column],
                                                      search_filters=["{}:in:{}".format(subscription.scoring_id_column, ",".join(scoring_ids))])

        return queue_table_rows

    def __save_explanations(self, store, subscription_id, explanation_task_ids):
        self.logger.info(
            "Getting explanations for the explantion task ids {} to store in datamart.".format(explanation_task_ids))

        search_filters = "subscription_id:eq:{},request_id:in:{}".format(subscription_id,
                                                                         ",".join(explanation_task_ids))
        response = store.get_explanations(
            search_filters=search_filters, order_by_column="finished_at:desc", limit=100)
        if explanation_task_ids and not response.get("values"):
            response = store.get_explanations(search_filters=search_filters)

        fields = response.get("fields")
        resp_values = response.get("values").copy()
        resp_values.sort(
            key=lambda x: x[fields.index("finished_at")], reverse=True)
        request_id_index = fields.index("request_id")
        values = []
        for tid in explanation_task_ids:
            exp_row = next(
                (v for v in resp_values if v[request_id_index] == tid), None)
            if exp_row:
                values.append(exp_row)

        if values:
            response["values"] = values

        self.save_data(self.arguments.get(
            "output_file_path")+"/explanations.json", response)
        self.logger.info(
            "Completed getting explanations to store in datamart.")
