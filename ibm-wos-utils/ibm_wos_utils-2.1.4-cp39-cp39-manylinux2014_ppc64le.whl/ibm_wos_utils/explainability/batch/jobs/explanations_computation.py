# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import sys
import base64
import uuid
import tarfile
import json
import datetime
from collections import OrderedDict
import pandas as pd
try:
    from pyspark import SparkFiles
    from pyspark.sql import Row, SparkSession
except ImportError as ie:
    pass

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.hive_utils import get_table_as_dataframe
from ibm_wos_utils.explainability.explainers.explainer import Explainer
from ibm_wos_utils.explainability.entity.explain_config import ExplainConfig
from ibm_wos_utils.explainability.batch.entity.subscription import Subscription
from ibm_wos_utils.explainability.entity.constants import Status


class ExplanationsComputation(AIOSBaseJob):

    def run_job(self):
        try:
            # Initialize attributes
            config, score_response = self.get_job_data()
            explain_config = self.get_explain_config(
                config.get("explainability_configuration"))
            subscription = Subscription(config.get("subscription"))

            # Read payload data
            payload_df = get_table_as_dataframe(spark=self.spark,
                                                database_name=subscription.database,
                                                table_name=subscription.payload_table, columns_to_map=self.__get_columns(
                                                    explain_config, subscription),
                                                columns_to_filter=[
                                                    subscription.scoring_id_column],
                                                record_timestamp_column=subscription.scoring_timestamp_column,
                                                start_time=self.arguments.get(
                                                    "start_time"),
                                                end_time=self.arguments.get("end_time"))
            self.logger.info("Got payload dataframe to compute explanations.")

            # Compute explanation and store response
            compute_explanation = ComputeExplanation(
                explain_config=explain_config, subscription=subscription, score_response=score_response)
            self.logger.info("Starting explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))

            if payload_df.rdd.isEmpty():
                self.logger.info(
                    "The payload records are empty. Hence skipping the run.")
            else:
                responses = payload_df.rdd.mapPartitions(
                    compute_explanation.compute).toDF()
                explanations_table = "{}.{}".format(
                    subscription.database, subscription.explanations_table)
                responses.write.mode("append").format(
                    "hive").saveAsTable(explanations_table)

            self.logger.info("Completed explanations computation task for subscription {} in datamart {}.".format(
                subscription.subscription_id, subscription.data_mart_id))
        except Exception as ex:
            self.logger.error(
                "An error occurred while running the explanations_computation job. " + str(ex))
            super().save_exception_trace(error_msg=str(ex))
        finally:
            pass

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
                             kernel_width=config.get("kernel_width")
                             )

    def get_job_data(self):
        print(self.arguments.get("data_file_path"))
        self.sc.addFile(self.arguments.get(
            "data_file_path") + "/explain_job_data.tar.gz")
        with tarfile.open(SparkFiles.get("explain_job_data.tar.gz")) as f:
            config = json.loads(f.extractfile("explain_config.json").read())
            perturbations_score_response = json.loads(
                f.extractfile("explain_scoring_response.json").read())

        return config, perturbations_score_response


class ComputeExplanation():

    def __init__(self, explain_config, subscription, score_response):
        self.explain_config = explain_config
        self.subscription = subscription
        self.score_response = score_response
        self.prediction = None
        self.probability = None

    def compute(self, data):

        def predict_proba(data):
            probabilities = self.score_response.get("probabilities")
            predictions = self.score_response.get("predictions")
            predictions[0] = self.prediction
            probabilities[0] = self.probability
            return self.score_response.get("predictions"), self.score_response.get("probabilities")

        explainer = Explainer(self.explain_config)
        for d in data:
            data_row = {f: d[f] for f in self.explain_config.feature_columns}
            data_row[self.explain_config.prediction_column] = d[self.explain_config.prediction_column]
            data_row[self.explain_config.probability_column] = d[self.explain_config.probability_column]
            self.prediction = d[self.explain_config.prediction_column]
            self.probability = d[self.explain_config.probability_column]

            explanations = explainer.explain(
                data_row=data_row, predict_proba=predict_proba)

            yield self.get_response_row(d, explanations)

    def get_response_row(self, row, explanations):

        time_stamp = self.__get_current_datetime()
        status = Status.ERROR.name if all(
            e.get("error") for e in explanations) else Status.FINISHED.name

        return Row(request_id=str(uuid.uuid4()),
                   scoring_id=row[self.subscription.scoring_id_column],
                   subscription_id=self.subscription.subscription_id,
                   data_mart_id=self.subscription.data_mart_id,
                   binding_id=self.subscription.binding_id,
                   deployment_id=self.subscription.deployment_id,
                   asset_name=self.subscription.asset_name,
                   deployment_name=self.subscription.deployment_name,
                   prediction=row[self.explain_config.prediction_column],
                   created_by="openscale",
                   created_at=time_stamp,
                   finished_at=time_stamp,
                   explanation_type=self.explain_config.explanation_types[0].value,
                   object_hash=self.__get_object_hash(row),
                   explanation=self.__encode_explanations(row, explanations),
                   status=status,
                   explanation_input="",
                   explanation_output="")

    def __encode_explanations(self, row, explanations):
        input_features = []
        for f in self.explain_config.feature_columns:
            input_features.append({"name": f,
                                   "value": row[f],
                                   "feature_type": "categorical" if f in self.explain_config.categorical_columns else "numerical"})

        entity = {"entity": {
            "asset": {
                "id": self.subscription.asset_id,
                "name": self.subscription.asset_name,
                "problem_type": self.explain_config.problem_type.value,
                "input_data_type": self.explain_config.input_data_type.value,
                "deployment": {
                    "id": self.subscription.deployment_id,
                    "name": self.subscription.deployment_name
                }
            },
            "input_features": input_features,
            "explanations": explanations
        }}
        return str(base64.b64encode(json.dumps(entity).encode("utf-8")))[2:-1]

    def __get_object_hash(self, row):
        feature_values = {f: row[f]
                          for f in self.explain_config.feature_columns}

        feature_values_sorted = OrderedDict(
            sorted(feature_values.items()))
        # convert the dict to a single row rectangular dataframe and get hash for first row
        feature_row_df = pd.DataFrame(feature_values_sorted, index=[0])
        return str(abs(pd.util.hash_pandas_object(
            feature_row_df, encoding="utf8").iloc[0]))

    def __get_current_datetime(self):
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
