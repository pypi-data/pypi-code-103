# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging

try:
    import pyspark.sql.functions as F
except ImportError as iex:
    pass

from datetime import datetime
from ibm_wos_utils.joblib.utils.constants import TIMESTAMP_FORMAT

logger = logging.getLogger(__name__)


def get_table_as_dataframe(
        spark,
        database_name: str,
        table_name: str,
        columns_to_map: list,
        columns_to_filter: list = [],
        record_timestamp_column: str = None,
        start_time: str = None,
        end_time: str = None):
    """Get Hive table as dataframe.

    Additionally, it does:
     - Converts any column of boolean type to string type
     - Maps the column names in the expected cases as specified in columns_to_map argument
     - Filter out header row based on columns_to_filter. Only uses the first column found in the table.
     - If provided, fetches records based on the timestamps

     It does NOT do any validation.

    Arguments:
        spark {SparkSession} -- Spark Session to use
        database_name {str} -- Name of Database in Hive
        table_name {str} -- Name of table in Hive
        columns_to_map {list} -- List of columns to map from lowercase to correct case

    Keyword Arguments:
        columns_to_filter {list} -- List of columns to filter out header row. Uses the first column found in table (default: {[]})
        record_timestamp_column {str} -- Name of the column with modeling role record-timestamp (default: {None})
        start_time {str} -- Start Time in ISO format `%Y-%m-%dT%H:%M:%S.%f` (default: {None})
        end_time {str} -- End Time in ISO format `%Y-%m-%dT%H:%M:%S.%f` (default: {None})

    Returns:
        pyspark Dataframe

    """
    sql_query = "select * from {}.{}".format(database_name, table_name)
    spark_df = spark.sql(sql_query)
    logger.info(spark_df.printSchema())
    logger.info(
        "******* Number of Partitions: {} ********".format(spark_df.rdd.getNumPartitions()))

    # Convert boolean columns to string
    spark_df_dtypes = dict(spark_df.dtypes)
    for col in spark_df.columns:
        if spark_df_dtypes[col] == "boolean":
            spark_df = spark_df.withColumn(
                col, spark_df[col].cast("string"))
            logger.info(
                " - Changed column {} of type boolean to type string.".format(col))

    # Convert columns in Hive in correct case
    lowercase_cols = list(
        map(lambda col: col.lower(), columns_to_map))
    column_mapping = {col: columns_to_map[lowercase_cols.index(
        col)] if col in lowercase_cols else col for col in spark_df.columns}
    spark_df = spark_df.select([F.col(old_col).alias(
        column_mapping[old_col]) for old_col in spark_df.columns])

    # Filter out the first row in case of csv and header is set
    column_to_filter = None
    for column in columns_to_filter:
        if column in spark_df.columns:
            column_to_filter = column
            break

    if column_to_filter is not None:
        table_properties = spark.sql(
            "show tblproperties {}.{}".format(
                database_name, table_name)).collect()
        logger.info(table_properties)
        property_keys = [row.key for row in table_properties]
        if ("skip.header.line.count" in property_keys):
            spark_df = spark_df.where(
                F.col(column_to_filter) != column_to_filter)
            logger.info("Property skip.header.line.count present in table_properties. Discarded first row using column {}".format(
                column_to_filter))

    if record_timestamp_column is not None and record_timestamp_column in spark_df.columns:
        # assumptions: start_time and end_time are in isoformat
        # %Y-%m-%dT%H:%M:%S.%fZ
        if start_time is not None:
            start_time = datetime.strptime(start_time, TIMESTAMP_FORMAT)
            spark_df = spark_df.where(
                F.col(record_timestamp_column) >= start_time)

        if end_time is not None:
            end_time = datetime.strptime(end_time, TIMESTAMP_FORMAT)
            spark_df = spark_df.where(
                F.col(record_timestamp_column) <= end_time)

    logger.info(spark_df.explain())
    logger.info(spark_df.printSchema())
    return spark_df
