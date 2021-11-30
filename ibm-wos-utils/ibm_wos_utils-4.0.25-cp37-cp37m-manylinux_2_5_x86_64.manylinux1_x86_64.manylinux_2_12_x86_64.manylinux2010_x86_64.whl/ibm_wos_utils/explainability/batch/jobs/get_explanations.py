# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.explainability.batch.utils.explanations_store import ExplanationsStore


class GetExplanations(AIOSBaseJob):
    """Spark job to get the explanations from hive"""

    def run_job(self):
        try:
            subscription_id = self.arguments.get(
                "subscription_id")
            self.logger.info(
                "Started get explanations job for subscription {}.".format(subscription_id))
            data_source = self.arguments.get("explain_data_source").copy()
            data_source["jdbc_connection_properties"] = self.jdbc_connection_properties

            store = ExplanationsStore(
                spark=self.spark, data_source=data_source, logger=self.logger)
            response = store.get_explanations(limit=self.arguments.get("limit"),
                                              offset=self.arguments.get(
                                                  "offset"),
                                              include_total_count=self.arguments.get(
                                                  "include_total_count"),
                                              column_filters=self.arguments.get(
                                                  "column_filters"),
                                              search_filters=self.arguments.get(
                                                  "search_filters"),
                                              order_by_column=self.arguments.get("order_by_column"))

            self.save_data(self.arguments.get(
                "output_file_path")+"/explanations.json", response)
            self.logger.info(
                "Completed get explanations job for subscription {}.".format(subscription_id))
        except Exception as ex:
            self.logger.error(
                "An error occurred while running the get explanations job. " + str(ex))
            super().save_exception_trace(error_msg=str(ex))
            raise ex
