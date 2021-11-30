# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import datetime
import json
import math
import random
import time
from operator import itemgetter
try:
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils import constants
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils


class BatchUtils():

    @classmethod
    def get_group_counts(cls, data, col_name: str, group_vals: list, fav_label_query: str, data_type) -> dict:
        """
        Returns the counts of the given group with it"s given classes counts.
        :data: The data on which the counts are to be counted. (from pyspark.sql.dataframe import DataFrame)
        :col_name: The column on which the counts are to be done.
        :group_vals: The group values/ranges for which the counts are to be made.
        :fav_label_query: The favourable label query.
        :data_type: The data type of the column
        """
        count_dict = {}
        # Getting the group rows
        if data_type in constants.CATEGORICAL_DATA_TYPES:
            all_groups_query = SQLUtils.get_cat_filter_query(
                col_name, "==", group_vals)
        elif data_type in constants.NUMERICAL_DATA_TYPES:
            all_groups_query = SQLUtils.get_num_filter_query(
                col_name, group_vals)
        else:
            raise ValueError(
                "Unknown data type {} encountered for {} column.".format(data_type, col_name))
        all_groups_df = data.filter(all_groups_query)

        # Getting the group counts
        for group in group_vals:
            group_query = ""
            # Getting the query for the current group
            if data_type in constants.CATEGORICAL_DATA_TYPES:
                group_query = SQLUtils.get_cat_filter_query(
                    col_name, "==", [group])
            elif data_type in constants.NUMERICAL_DATA_TYPES:
                group_query = SQLUtils.get_num_filter_query(col_name, [group])
            else:
                raise ValueError(
                    "Unknown data type {} encountered for {} column.".format(data_type, col_name))

            # Getting applying filter to get current group rows
            group_df = all_groups_df.filter(group_query)
            group_fav_count = group_df.filter(fav_label_query).count()
            group_count = group_df.count()
            count_dict[str(group)] = {
                "fav_count": group_fav_count,
                "total_count": group_count
            }
        return count_dict

    @classmethod
    def calculate_di_variables(cls, data, fairness_attribute: str, inputs: dict, data_type, model_type: str) -> dict:
        """
        Calculates the variables needed for disparate impact calculation on the given fairness attribute.
        :data: The data on which the variables are to be calculated. (from pyspark.sql.dataframe import DataFrame)
        :fairness_attribute: The fairness attribute on which the variables are to be calculated.
        :inputs: The inputs dictionary.
        :data_type: The data type of the fairness attribute column.
        """
        di_vars = {
            "majority": {},
            "minority": {}
        }
        # Getting the majority and minority groups
        majority = get(inputs, "majority.{}".format(fairness_attribute))
        minority = get(inputs, "minority.{}".format(fairness_attribute))
        # Getting the label column and favourable outcomes
        label_column = get(inputs, "class_label")
        fav_classes = get(inputs, "favourable_class")

        # Getting the query for favourable outcome rows
        favorable_count_query = None
        if model_type == constants.REGRESSION_MODEL_TYPE:
            favorable_count_query = SQLUtils.get_num_filter_query(
                label_column, fav_classes)
        else:
            favorable_count_query = SQLUtils.get_cat_filter_query(
                label_column, "==", fav_classes)

        # Getting the counts for majority
        di_vars["majority"] = cls.get_group_counts(
            data, fairness_attribute, majority, favorable_count_query, data_type)

        # Getting the counts for minorities
        di_vars["minority"] = cls.get_group_counts(
            data, fairness_attribute, minority, favorable_count_query, data_type)
        return di_vars

    @classmethod
    def calculate_di_dict(cls, data, inputs: dict, data_types: dict, model_type: str) -> dict:
        """
        Returns a dictionary with disparate impact variables for the given data for all fairness attributes in the given inputs.
        :data: The data on which the disparate impact variables are to be calculated. (from pyspark.sql.dataframe import DataFrame)
        :inputs: The inputs dictionary.
        :data_types: The data types of the fairness attributes.
        :model_type: The model type.
        """
        di_dict = {}

        # Getting all labels
        all_labels = get(inputs, "favourable_class") + get(inputs, "unfavourable_class")
        label_column = get(inputs, "class_label")

        # Filtering unused label rows
        if model_type == constants.REGRESSION_MODEL_TYPE:
            all_label_query = SQLUtils.get_num_filter_query(label_column, all_labels)
        else:
            all_label_query = SQLUtils.get_cat_filter_query(label_column, "==", all_labels)
        
        # Applying the query
        data = data.filter(all_label_query)

        for fairness_attribute in inputs["fairness_attributes"]:
            data_type = data_types[fairness_attribute] if fairness_attribute in data_types else None
            # Calculating the DI variables on the given data
            di_dict[fairness_attribute] = cls.calculate_di_variables(
                data, fairness_attribute, inputs, data_type, model_type)
        # Add rows analyzed
        di_dict = cls.add_rows_analyzed(di_dict, data, inputs, data_types)
        return di_dict

    @classmethod
    def get_inputs_from_monitor_instance(cls, monitor_instance: dict) -> dict:
        """
        Converts the given fairness configuration into the inputs dictionary.
        :monitor_instance: The fairness configuration dictionary.
        """
        inputs = {}
        parameters = get(monitor_instance, "entity.parameters")
        inputs["class_label"] = get(parameters, "class_label")
        inputs["favourable_class"] = get(parameters, "favourable_class")
        inputs["unfavourable_class"] = get(parameters, "unfavourable_class")
        inputs["min_records"] = get(parameters, "min_records")
        majority = {}
        minority = {}
        fairness_attributes = []
        threshold = []
        features = get(parameters, "features")
        if features is not None:
            for feature_details in features:
                feature = get(feature_details, "feature")
                if feature is not None:
                    fairness_attributes.append(feature)
                    threshold.append(get(feature_details, "threshold"))
                    majority[feature] = get(feature_details, "majority")
                    minority[feature] = get(feature_details, "minority")
        inputs["majority"] = majority
        inputs["minority"] = minority
        inputs["threshold"] = threshold
        inputs["fairness_attributes"] = fairness_attributes
        return inputs

    @classmethod
    def get_data_source_from_subscription(cls, subscription: dict, data_source_type: str) -> dict:
        """
        Parses the subscription and returns the given data source type.
        :subscription: The subscription JSON.
        :data_source_type: The data source type to be returned.
        """
        data_source = None
        data_sources = get(subscription, "entity.data_sources")
        for ds in data_sources:
            if ds["type"] == data_source_type:
                data_source = ds
                break
        return data_source

    @classmethod
    def get_data_types(cls, subscription: dict, fairness_attributes: list) -> dict:
        """
        Parses the subscription JSON and returns the data types of the given fairness attribute.
        :subscription: The subscription JSON.
        :fairness_attributes: The list of fairness attributes.
        """
        data_types = {}

        # Getting the fields array from the output data schema
        fields = get(
            subscription, "entity.asset_properties.output_data_schema.fields")
        for field in fields:
            field_name = field["name"]
            if field_name in fairness_attributes:
                data_types[field_name] = field["type"]

        return data_types

    @classmethod
    def check_if_modeling_role_present(cls, modeling_role: str, schema: dict) -> bool:
        """
        Checks if the given modeling role is present in the given schema.
        :modeling_role: The modeling role to be checked.
        :schema: The schema in which the modeling role is to be searched.
        """
        is_present = False

        for field in schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            if field_modeling_role and field_modeling_role == modeling_role:
                is_present = True
                break
        return is_present

    @classmethod
    def get_name_with_modeling_role(cls, modeling_role: str, schema: dict) -> str:
        """
        Returns the name of the column with the given modeling role in the given schema.
        :modeling_role: The modeling role to be checked.
        :schema: The schema in which the column name is to be searched.
        """
        col_name = None

        for field in schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            if field_modeling_role and field_modeling_role == modeling_role:
                col_name = field["name"]
                break
        return col_name

    @classmethod
    def add_rows_analyzed(cls, di_dict: dict, data, inputs: dict, data_types: dict) -> dict:
        """
        Calculates and adds rows analyzed from the DI variable values.
        :di_dict: The DI dictionary.
        :data: The data on which the disparate impact variables are calculated. (from pyspark.sql.dataframe import DataFrame)
        :inputs: The inputs dictionary.
        :data_types: The data types of the fairness attributes.
        """
        global_rows_analyzed = None

        # Figuring out the attribute with highest rows analyzed
        max_row_fair_att = None
        max_rows_analyzed = None
        for fairness_attribute in di_dict:
            fa_di_dict = di_dict[fairness_attribute]
            # Calcuating the rows analyzed for this fairness attribute
            fa_rows_analyzed = 0

            # Adding the minority counts
            min_dict = fa_di_dict["minority"]
            for min_group in min_dict:
                fa_rows_analyzed += min_dict[min_group]["total_count"]

            # Adding the majority counts
            maj_dict = fa_di_dict["majority"]
            for maj_group in maj_dict:
                fa_rows_analyzed += maj_dict[maj_group]["total_count"]

            # Adding rows analyzed for the fairness attribute
            fa_di_dict["rows_analyzed"] = fa_rows_analyzed

            # Updating the max rows fairness attribute
            if max_row_fair_att is None:
                max_row_fair_att = fairness_attribute
                max_rows_analyzed = fa_rows_analyzed
            else:
                if fa_rows_analyzed > max_rows_analyzed:
                    max_row_fair_att = fairness_attribute
                    max_rows_analyzed = fa_rows_analyzed
        
        # Calculating the global rows analyzed #20703
        # Getting the count of unused groups for this attribute
        data_type = data_types[max_row_fair_att]
        all_used_groups = get(inputs, "majority.{}".format(max_row_fair_att)) + get(inputs, "minority.{}".format(max_row_fair_att))
        if data_type in constants.CATEGORICAL_DATA_TYPES:
            # The attribute is categorical
            unused_group_query = SQLUtils.get_cat_filter_query(max_row_fair_att, "!=", all_used_groups, concat_operator="and")
            unused_rows_fair_att = data.filter(unused_group_query).count()
        else:
            # The attribute is numerical
            unused_group_query = SQLUtils.get_num_filter_query(max_row_fair_att, all_used_groups, include=False, concat_operator="and")
            unused_rows_fair_att = data.filter(unused_group_query).count()
        
        print("Unused rows for max rows analyzed fairness attribute were found to be {}".format(unused_rows_fair_att))
        global_rows_analyzed = max_rows_analyzed + unused_rows_fair_att
        print("Global rows analyzed is {}".format(global_rows_analyzed))

        # Adding the global rows analyzed
        di_dict["rows_analyzed"] = global_rows_analyzed
        return di_dict

    @classmethod
    def merge_di_dicts(cls, di_dict_1: dict, di_dict_2: dict) -> dict:
        """
        Adds up the numbers from the given DI dictionaries and returns a combined one.
        :di_dict_1: The first DI dictionary.
        :di_dict_2: The second DI dictionary.
        """
        di_dict = {}

        # Adding the numbers for each of the fairness attributes given
        for key in di_dict_1:
            if key == "rows_analyzed":
                di_dict["rows_analyzed"] = di_dict_1["rows_analyzed"] + \
                    di_dict_2["rows_analyzed"]
            else:
                # Calculating the summed majority
                summed_majority = {}
                for maj in di_dict_1[key]["majority"]:
                    summed_majority[maj] = {
                        "fav_count": di_dict_1[key]["majority"][maj]["fav_count"] + di_dict_2[key]["majority"][maj]["fav_count"],
                        "total_count": di_dict_1[key]["majority"][maj]["total_count"] + di_dict_2[key]["majority"][maj]["total_count"]
                    }
                # Calculating the summed minority
                summed_minority = {}
                for mino in di_dict_2[key]["minority"]:
                    summed_minority[mino] = {
                        "fav_count": di_dict_1[key]["minority"][mino]["fav_count"] + di_dict_2[key]["minority"][mino]["fav_count"],
                        "total_count": di_dict_1[key]["minority"][mino]["total_count"] + di_dict_2[key]["minority"][mino]["total_count"]
                    }
                di_dict[key] = {
                    "majority": summed_majority,
                    "minority": summed_minority,
                    "rows_analyzed": di_dict_1[key]["rows_analyzed"] + di_dict_2[key]["rows_analyzed"]
                }

        return di_dict
    
    @classmethod
    def get_batch_data_distribution(cls, data_counts: dict, monitor_instance: dict) -> dict:
        """
        Generates the distribution (fav/unfav counts only) for the given counts.

        :data_counts: the counts for the given data.
        :monitor_instance: The monitor instance object.

        :returns: The distribution object.
        """
        data_distribution = None

        # Generating the values
        values = []
        for feature in get(monitor_instance, "entity.parameters.features"):
            fairness_attribute = get(feature, "feature")
            
            # Getting the counts for the fairness attribute
            att_counts = get(data_counts, "counts.{}".format(fairness_attribute))

            # Adding the majority counts
            majority = get(feature, "majority")
            maj_counts = get(att_counts, "majority")
            for maj in majority:
                # Getting the counts
                fav_count = get(maj_counts, "{}.fav_count".format(str(maj)))
                total_count = get(maj_counts, "{}.total_count".format(str(maj)))
                unfav_count = total_count - fav_count
                
                values.append([
                    fairness_attribute,
                    maj,
                    fav_count,
                    unfav_count,
                    "reference"
                ])
            
            # Adding the minority counts
            minority = get(feature, "minority")
            mino_counts = get(att_counts, "minority")
            for mino in minority:
                # Getting the counts
                fav_count = get(mino_counts, "{}.fav_count".format(str(mino)))
                total_count = get(mino_counts, "{}.total_count".format(str(mino)))
                unfav_count = total_count - fav_count

                values.append([
                    fairness_attribute,
                    mino,
                    fav_count,
                    unfav_count,
                    "monitored"
                ])

        data_distribution = {
            "fields": [
                "feature",
                "feature_value",
                "fav_count",
                "unfav_count",
                "group"
            ],
            "values": values
        }

        return data_distribution
    
    @classmethod
    def get_spark_settings_from_subscription(cls, subscription: dict) -> dict:
        """
        Returns the spark settings from the given subscription object.
        :subscription: The subscription object.
        """
        spark_settings = None
        spark_settings = get(
            subscription, "entity.analytics_engine.parameters")
        return spark_settings
