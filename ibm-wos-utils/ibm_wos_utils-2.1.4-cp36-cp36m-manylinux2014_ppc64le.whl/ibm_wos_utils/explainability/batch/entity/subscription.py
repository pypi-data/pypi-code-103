# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class Subscription():

    def __init__(self, subscription):
        subscription = subscription or {}

        # Connection details
        data_source = subscription.get("data_source") or {}
        self.database_type = data_source.get("type")
        self.database = data_source.get("database_name")
        self.schema = data_source.get("schema_name")
        self.explanations_table = data_source.get(
            "parameters").get("result_table_name")
        self.payload_table = data_source.get("table_name")

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
