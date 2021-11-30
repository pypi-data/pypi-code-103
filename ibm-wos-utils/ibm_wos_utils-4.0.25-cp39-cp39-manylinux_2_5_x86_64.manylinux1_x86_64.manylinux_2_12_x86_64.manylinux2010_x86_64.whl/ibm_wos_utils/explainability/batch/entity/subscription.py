# ----------------------------------------------------------------------------------------------------# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class Subscription():

    def __init__(self, subscription):
        subscription = subscription or {}

        # Explanation connection details
        explain_data_source = subscription.get("explain_data_source") or {}
        self.explanations_db_conn = explain_data_source.get("connection") or {}
        self.explanations_db_type = self.explanations_db_conn.get("type")
        self.explanations_db_location_type = self.explanations_db_conn.get(
            "location_type")
        self.explanations_db_name = explain_data_source.get("database_name")
        self.result_table_name = explain_data_source.get("result_table_name")
        self.queue_table = explain_data_source.get("table_name")
        self.explanations_db_schema = explain_data_source.get(
            "schema_name")
        self.queue_partition_column = explain_data_source.get(
            "partition_column")
        self.queue_num_partitions = explain_data_source.get("num_partitions")

        # Payload connection details
        payload_data_source = subscription.get("payload_data_source") or {}
        self.payload_db_conn = payload_data_source.get("connection")
        self.payload_db_name = payload_data_source.get("database_name")
        self.payload_table = payload_data_source.get("table_name")
        self.payload_db_schema = payload_data_source.get("schema_name")
        self.payload_partition_column = payload_data_source.get(
            "partition_column")
        self.payload_num_partitions = payload_data_source.get("num_partitions")

        # Subscription details
        self.data_mart_id = subscription.get("data_mart_id")
        self.subscription_id = subscription.get("subscription_id")
        self.binding_id = subscription.get("binding_id")

        asset = subscription.get("asset") or {}
        self.asset_name = asset.get("name")
        self.asset_id = asset.get("id")

        deployment = subscription.get("deployment") or {}
        self.deployment_name = deployment.get("name")
        self.deployment_id = deployment.get("id")

        self.scoring_id_column = subscription.get("scoring_id_column")
        self.scoring_timestamp_column = subscription.get(
            "scoring_timestamp_column")

    def __str__(self):
        subscription_dict = vars(self).copy()
        del subscription_dict["explanations_db_conn"]
        del subscription_dict["payload_db_conn"]
        return str(subscription_dict)
