# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
The fairness configuration and data distribution builder for common configuration job.
"""
try:
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils

class FairnessConfigDistributionBuilder():

    def __init__(self, common_configuration: dict, fairness_parameters: dict, training_df):
        """
        Constructor for the class.
        :common_configuration: The common configuration.
        :parameters: The fairness parameters.
        :training_df: The training data in a spark data frame. (from pyspark.sql.dataframe import DataFrame)
        """
        self.common_configuration = common_configuration
        self.parameters = fairness_parameters
        self.training_df = training_df
    
    def build(self) -> dict:
        """
        Builds the fairness configuration and the training data distribution as per the given parameters.

        :returns: The fairness configuration.
        """
        start_time = DateUtil.current_milli_time()
        fairness_configuration = None

        # Validating the fairness parameters
        self._validate_parameters()
        print("Validated the fairness parameters successfully.")

        # Building a mock monitor instance and subscription object for re-using main service code
        monitor_instance = {
            "entity": {
                "parameters": self.parameters
            }
        }
        subscription = {
            "entity": {
                "asset_properties": self.common_configuration
            }
        }

        # Getting the inputs and data types dictionary
        inputs = BatchUtils.get_inputs_from_monitor_instance(monitor_instance)
        data_types = BatchUtils.get_data_types(subscription, inputs["fairness_attributes"])

        # Getting the model type
        model_type = get(self.common_configuration, "problem_type")


        # Getting the DI dict
        counts_dict = BatchUtils.calculate_di_dict(self.training_df, inputs, data_types, model_type)
        di_dict = {
            "data_name": "training",
            "counts": counts_dict
        }
        print("Calculated the DI counts for the training data.")

        # Getting the training data distribution
        training_data_distribution = BatchUtils.get_batch_data_distribution(di_dict, monitor_instance)
        print("Generated the distribution JSON for the training data.")

        training_data_rows_count = get(di_dict, "counts.rows_analyzed")

        # Generating the thresholds
        specific_values = []
        for feature in get(self.parameters, "features"):
            feature_specific_value = {}
            feature_specific_value["value"] = float(get(feature, "threshold")) * 100
            feature_specific_value["applies_to"] = [
                {
                    "type": "tag",
                    "key": "feature",
                    "value": get(feature, "feature")
                }
            ]
            specific_values.append(feature_specific_value)
        
        thresholds = [
            {
                "metric_id": "fairness_value",
                "type": "lower_limit",
                "value": 80,
                "specific_values": specific_values
            }
        ]


        # Building the fairness configuration
        fairness_configuration = {
            "parameters": {
                "features": get(self.parameters, "features"),
                "favourable_class": get(self.parameters, "favourable_class"),
                "unfavourable_class": get(self.parameters, "unfavourable_class"),
                "training_data_distributions": training_data_distribution,
                "training_data_records_count": training_data_rows_count,
                "training_data_class_label": get(self.parameters, "class_label"),
                "training_data_last_processed_time": DateUtil.get_current_datetime(),
                "training_data_measurements_computed": False
            },
            "thresholds": thresholds
        }

        # Adding min_records if present #20528
        min_records = get(self.parameters, "min_records")
        if min_records is not None:
            fairness_configuration["parameters"]["min_records"] = min_records

        time_taken = DateUtil.current_milli_time() - start_time
        print("Time taken to build the fairness configuration and training data distribution for {} rows was {} seconds.".format(training_data_rows_count, time_taken/1000))
        return fairness_configuration
       
    def _validate_parameters(self) -> None:
        """
        Validates the fairness parameters set in the class object.

        :returns: None
        """

        # Validating the first level keys
        first_level_keys = [
            "features",
            "class_label",
            "favourable_class",
            "unfavourable_class",
            "min_records"
        ]
        for key in first_level_keys:
            if key not in self.parameters and key != "min_records":
                raise Exception("Mandatory field {} not provided in the parameters.".format(key))
        
        # Validating the min_records if present
        if "min_records" in self.parameters:
            min_records = get(self.parameters, "min_records")
            if min_records is not None and not isinstance(min_records, int):
                raise Exception("Minimum records needed for fairness calculation must be an integer.")
        
        # Validating fav/unfav classes
        fav_classes = get(self.parameters, "favourable_class")
        if not isinstance(fav_classes, list):
            raise Exception("Favourable classes must be provided in a list.")
        unfav_classes = get(self.parameters, "unfavourable_class")
        if not isinstance(unfav_classes, list):
            raise Exception("Unfavourable classes must be provided in a list.")

        # Validating the class label
        class_label = get(self.parameters, "class_label")
        if not isinstance(class_label, str):
            raise Exception("The name of the label column must be a string.")

        # Validating the features
        features = get(self.parameters, "features")
        if not isinstance(features, list):
            raise Exception("The feature details should be given in a list.")

        feature_details = [
            "feature",
            "majority",
            "minority",
            "threshold"
        ]
        for feature in features:
            for detail in feature_details:
                if detail not in feature and detail != "threshold":
                    raise Exception("Mandatory feature detail {} not provided.".format(detail))
            
            # Validating the threshold
            if "threshold" in feature:
                threshold = get(feature, "threshold")
                if not isinstance(threshold, float) or threshold < 0.0 or threshold > 1.0:
                    raise Exception("Threshold should be a float number between 0 and 1.")
            
            # Validating the attribute name
            fairness_attribute = get(feature, "feature")
            if not isinstance(fairness_attribute, str):
                raise Exception("The feature name which is to be monitored must be a string.")

            # Validating the majority and minority
            majority = get(feature, "majority")
            minority = get(feature, "minority")
            if not isinstance(majority, list):
                raise Exception("The majority groups must be provided in a list.")
            if not isinstance(minority, list):
                raise Exception("The minority groups must be provided in a list.")

        return