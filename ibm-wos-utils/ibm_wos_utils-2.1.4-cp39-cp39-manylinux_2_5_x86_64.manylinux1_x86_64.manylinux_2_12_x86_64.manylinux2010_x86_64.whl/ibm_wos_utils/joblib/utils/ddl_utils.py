# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import collections
import uuid
import json
import tempfile
import tarfile

from ibm_wos_utils.joblib.utils.param_utils import get

# Mapping between Hive and Spark data types. Data types like "float",
# "double" which are present in both are not added
spark_to_hive_map = {
    "byte": "tinyint",
    "short": "smallint",
    "integer": "int",
    "long": "bigint",
    "calendarinterval": "interval"
}


def __generate_table_name(prefix, suffix=None):
    return "{}_table_{}".format(
        prefix, suffix or str(
            uuid.uuid4())).replace(
        "-", "")


def __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name: str = None,
        path_to_hdfs_directory: str =None,
        stored_as: str = "csv",
        table_properties: dict = {}):

    column_string = "("
    collection_items = False

    for field in ddl_fields:
        feature_name = field.get("name")
        feature_type = field.get("type")

        # for columns with the type stored in a dictionary, prepare column type
        # as a string
        if isinstance(feature_type, collections.Mapping):
            data_type = feature_type.get("type")
            element_type = feature_type.get("elementType")
            hive_element_type = spark_to_hive_map.get(
                element_type, element_type)
            feature_type = "{}<{}>".format(data_type, hive_element_type)
            collection_items = True
        else:
            hive_element_type = spark_to_hive_map.get(feature_type)
            if hive_element_type is not None:
                feature_type = hive_element_type

        column_string += "`{}` {}, ".format(feature_name, feature_type)

    ddl_column_string = column_string[:-2] + ")"

    if database_name:
        ddl_string = "CREATE TABLE IF NOT EXISTS {}.{} {}".format(
            database_name, table_name, ddl_column_string)
    else:
        ddl_string = "CREATE TABLE IF NOT EXISTS {} {}".format(
            table_name, ddl_column_string)

    if stored_as == "csv":
        ddl_string += " ROW FORMAT DELIMITED FIELDS TERMINATED BY ','"
        if collection_items:
            ddl_string += " COLLECTION ITEMS TERMINATED BY '|'"
        ddl_string += " STORED AS TEXTFILE "
    elif stored_as == "parquet":
        ddl_string += " STORED AS PARQUET "
    elif stored_as == "orc":
        ddl_string += " STORED AS ORC "
    else:
        raise Exception(
            "Unsupported storage format '{}' specified.".format(stored_as))

    if path_to_hdfs_directory is not None and path_to_hdfs_directory != "":
        ddl_string += " LOCATION '{}'".format(
            path_to_hdfs_directory)

    if table_properties:
        table_properties_arr = []
        for key, value in table_properties.items():
            table_properties_arr.append("'{}'='{}'".format(key, value))
        ddl_string += " TBLPROPERTIES ({})".format(
            ",".join(table_properties_arr))

    return ddl_string + ";"


def generate_payload_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "payload",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {}):
    """Generates Create DDL statement for Payload Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"payload"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})

    Returns:
        str -- Create DDL statement for Payload Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = [field for field in common_configuration.get("training_data_schema")[
        "fields"] if get(field, "metadata.modeling_role") != "target"]

    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction",
            "record-timestamp",
                "record-id"):
            ddl_fields.append(field)

    return __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)


def generate_feedback_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "feedback",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {}):
    """Generates Create DDL statement for Feedback Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"feedback"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})

    Returns:
        str -- Create DDL statement for Feedback Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = common_configuration.get(
        "training_data_schema")["fields"].copy()

    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction",
            "record-timestamp",
                "record-id"):
            ddl_fields.append(field)

    return __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)


def generate_scored_training_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "scored_training",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {}):
    """Generates Create DDL statement for Scored Training Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"feedback"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})

    Returns:
        str -- Create DDL statement for Scored Training Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = common_configuration.get(
        "training_data_schema")["fields"].copy()

    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction"):
            ddl_fields.append(field)

    return __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)

def generate_drift_table_ddl(
        drift_archive: bytearray,
        database_name: str = None,
        table_prefix: str = "drifted_transactions",
        table_suffix: str = None):
    """Generates Create DDL statement for Drifted Transactions Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        drift_archive {bytearray} -- Drift Archive

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"drifted_transactions"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.

    Returns:
        str -- Create DDL statement for Drifted Transactions Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(drift_archive)
        tmp_file.flush()
        with tarfile.open(tmp_file.name, "r:gz") as tf:
            with tf.extractfile("drifted_transactions_schema.json") as json_data:
                schema = json.load(json_data)
    columns = schema["columns"]

    ddl_fields = [{"name": key, "type": columns[key]["type"]}
                  for key in columns]
    return __generate_table_ddl(ddl_fields, table_name=table_name, database_name=database_name)
