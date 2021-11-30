# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from datetime import datetime
from abc import abstractmethod
try:
    from pyspark.sql.types import StructField, StructType, StringType, TimestampType, FloatType, BinaryType
except ImportError as e:
    pass

from ibm_wos_utils.explainability.utils.date_time_util import DateTimeUtil
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class ExplanationsStore():
    """Class used to store and retrieve explanations."""

    def __init__(self, spark, data_source, logger):
        self.logger = logger
        self.data_store = self.__get_data_store(spark, data_source, logger)

    def store_explanations(self, explanations):
        self.data_store.store_explanations(explanations)

    def get_explanations(self, limit=None, offset=None,
                         include_total_count=None,
                         column_filters=None,
                         search_filters=None,
                         order_by_column=None):
        fields, values, total_count = self.data_store.get_explanations(limit=limit,
                                                                       offset=offset, include_total_count=include_total_count,
                                                                       column_filters=column_filters,
                                                                       search_filters=search_filters,
                                                                       order_by_column=order_by_column)

        response = {"fields": fields}
        if values:
            response["values"] = values
        if total_count:
            response["total_count"] = total_count

        self.logger.info("Explanations response: "+str(response))
        return response

    def __get_data_store(self, spark, data_source, logger):
        data_stores = [HiveDataStore(spark, data_source, logger),
                       JdbcDataStore(spark, data_source, logger)]

        return next((d for d in data_stores if d.is_supported()), None)


class DataStore():
    """Interface for the different types of data stores"""

    def __init__(self, spark, data_source, logger):
        self.spark = spark
        self.data_source = data_source
        self.store_type = data_source["connection"]["type"]
        self.logger = logger

    @abstractmethod
    def is_supported(self):
        pass

    @abstractmethod
    def store_explanations(self, explanations):
        pass

    @abstractmethod
    def get_explanations(self, limit=None, offset=None,
                         include_total_count=None,
                         column_filters=None,
                         search_filters=None,
                         order_by_column=None):
        pass

    @staticmethod
    def get_explanations_schema():
        """Schema of the explanation rows stored"""
        schema = StructType([StructField("request_id", StringType(), False),
                             StructField("scoring_id", StringType(), False),
                             StructField("subscription_id",
                                         StringType(), True),
                             StructField("data_mart_id", StringType(), True),
                             StructField("binding_id", StringType(), True),
                             StructField("deployment_id", StringType(), True),
                             StructField("asset_name", StringType(), True),
                             StructField("deployment_name",
                                         StringType(), True),
                             StructField("prediction", StringType(), True),
                             StructField("created_by", StringType(), True),
                             StructField("created_at", TimestampType(), True),
                             StructField("finished_at", TimestampType(), True),
                             StructField("explanation_type",
                                         StringType(), True),
                             StructField("object_hash", StringType(), True),
                             StructField("explanation", BinaryType(), True),
                             StructField("status", StringType(), True),
                             StructField("explanation_input",
                                         BinaryType(), True),
                             StructField("explanation_output",
                                         BinaryType(), True),
                             StructField("error", BinaryType(), True),
                             StructField("probability", FloatType(), True)])
        return StructType(sorted(schema, key=lambda f: f.name))


class HiveDataStore(DataStore):
    """Hive data store implementation, which stores and retrieves explanations in hive orc format"""

    def __init__(self, spark, data_source, logger):
        super().__init__(spark, data_source, logger)
        self.database = self.data_source.get("database_name")
        self.table = self.data_source.get("result_table_name")

    def is_supported(self):
        if self.store_type == "hive":
            return True

        return False

    def store_explanations(self, explanations):
        start_time = DateTimeUtil.current_milli_time()
        responses_df = self.spark.createDataFrame(
            explanations, self.get_explanations_schema())
        explanations_table = "{}.{}".format(self.database, self.table)
        self.logger.info(
            "Storing explanations in {}".format(explanations_table))
        responses_df.write.mode("append").insertInto(explanations_table)
        self.logger.info("Completed storing explanations in {} ms.".format(
            DateTimeUtil.current_milli_time()-start_time))

    def get_explanations(self, limit=None, offset=None,
                         include_total_count=None,
                         column_filters=None,
                         search_filters=None,
                         order_by_column=None):
        start_time = DateTimeUtil.current_milli_time()

        explanations_query = self.__get_explanations_query(limit=limit,
                                                           offset=offset,
                                                           column_filters=column_filters,
                                                           search_filters=search_filters,
                                                           order_by_column=order_by_column)
        self.logger.info(
            "Executing query {}.".format(explanations_query))
        explanations_df = self.spark.sql(explanations_query)
        explanations = explanations_df.collect()
        self.logger.info("Completed query execution in {} ms".format(
            DateTimeUtil.current_milli_time()-start_time))

        fields = explanations_df.columns
        values, total_count = self.__get_values_and_total_count(
            explanations=explanations, fields=fields, limit=limit, offset=offset, include_total_count=include_total_count,
            search_filters=search_filters)

        return fields, values, total_count

    def __get_explanations_query(self, limit=None, offset=None,
                                 column_filters=None,
                                 search_filters=None,
                                 order_by_column=None):
        column_filters = "*" if not column_filters else column_filters
        conditions = self.__get_conditions_from_search_filters(search_filters)

        if order_by_column and limit and offset:
            fs = order_by_column.split(":")
            if fs[1] == "desc":
                order_by = "{} {}".format(fs[0], "DESC")
            else:
                order_by = fs[0]

            query = "with result as ( SELECT {}, ROW_NUMBER() OVER (ORDER BY {}) AS row_number FROM {}.{} WHERE {}) select {} from result where row_number >= {} and row_number < {}".format(
                column_filters, order_by, self.database, self.table, conditions, column_filters, offset, offset+limit)
        else:
            query = "SELECT {} FROM {}.{} WHERE {}".format(
                column_filters, self.database, self.table, conditions)

            if order_by_column and limit:
                fs = order_by_column.split(":")
                query = "{} ORDER BY {} {}".format(query, fs[0], fs[1].upper())

                limit = min(limit, 100)
                query = "{} LIMIT {}".format(query, limit)

        return query

    def __get_total_count_query(self, search_filters):
        conditions = self.__get_conditions_from_search_filters(search_filters)
        return "SELECT COUNT(*) AS explanations_count FROM {}.{} WHERE {}".format(
            self.database, self.table, conditions)

    def __get_values_and_total_count(self, explanations, fields, limit=None, offset=None, include_total_count=None, search_filters=None):
        values = []
        total_count = 0
        for row in explanations:
            values_row = []
            for f in fields:
                val = row[f]
                if val and isinstance(val, datetime):
                    val = DateTimeUtil.get_datetime_iso_format(val)
                if val and isinstance(val, bytearray):
                    val = val.decode("utf-8")
                values_row.append(val)
            values.append(values_row)

        if include_total_count:
            if len(values) < limit and offset is not None and int(offset) == 0:
                total_count = len(values)
            else:
                total_count_query = self.__get_total_count_query(
                    search_filters)
                start_time = DateTimeUtil.current_milli_time()
                self.logger.info(
                    "Executing query {}.".format(total_count_query))
                rows = self.spark.sql(total_count_query).collect()
                self.logger.info("Completed query execution in {} ms".format(
                    DateTimeUtil.current_milli_time()-start_time))
                total_count = rows[0]["explanations_count"]

        return values, total_count

    def __get_conditions_from_search_filters(self, search_filters):
        conditions_str = ""
        if search_filters:
            conditions = []
            filters = search_filters.split(",")
            for f in filters:
                fs = f.split(":")
                column = fs[0]
                operator = fs[1]
                value = ":".join(fs[2:])
                if operator == "eq":
                    conditions.append("{}='{}'".format(column, value))
                elif operator == "in":
                    values = ",".join(["'{}'".format(x)
                                       for x in value.split(",")])
                    conditions.append("{} IN ({})".format(column, values))
                elif operator == "le":
                    conditions.append("{} <= '{}'".format(column, value))
                elif operator == "ge":
                    conditions.append("{} >= '{}'".format(column, value))

            if conditions:
                conditions_str = " AND ".join(conditions)

        return conditions_str


class JdbcDataStore(DataStore):

    def __init__(self, spark, data_source, logger):
        super().__init__(spark, data_source, logger)
        self.database = self.data_source.get("database_name")
        connection = self.data_source.get("connection")
        self.location_type = connection.get("location_type")
        self.schema_name = self.data_source.get("schema_name")
        self.table = self.data_source.get("result_table_name")
        self.connection_properties = self.data_source.get(
            "jdbc_connection_properties")
        self.logger = logger
        self.spark = spark

    def store_explanations(self, explanations):
        start_time = DateTimeUtil.current_milli_time()
        self.logger.info("Writing explanations data frame to {}.{} in db2".format(
            self.schema_name, self.table))
        responses_df = self.spark.createDataFrame(
            explanations, self.get_explanations_schema())
        DbUtils.write_dataframe_to_table(
            spark_df=responses_df,
            location_type=self.location_type,
            database_name=self.database,
            schema_name=self.schema_name,
            table_name=self.table,
            connection_properties=self.connection_properties,
            spark=self.spark
        )
        end_time = DateTimeUtil.current_milli_time()
        self.logger.info("Completed writing explanations to the table {}.{}".format(
            self.schema_name, self.table))
        self.logger.info(
            "Time taken to write the explanations to db2 is {}".format(end_time-start_time))

    def is_supported(self):
        if self.store_type == "jdbc":
            return True

        return False

    def get_explanations(self, limit=None, offset=None,
                         include_total_count=None,
                         column_filters=None,
                         search_filters=None,
                         order_by_column=None):
        start_time = DateTimeUtil.current_milli_time()

        explanations_query = self.__get_explanations_query(limit=limit,
                                                           offset=offset,
                                                           column_filters=column_filters,
                                                           search_filters=search_filters,
                                                           order_by_column=order_by_column)
        self.logger.info(
            "Executing query {}.".format(explanations_query))
        explanations_df = DbUtils.get_table_as_dataframe(spark=self.spark,
                                                         location_type=self.location_type,
                                                         database_name=self.database,
                                                         table_name=self.table,
                                                         schema_name=self.schema_name,
                                                         connection_properties=self.connection_properties,
                                                         sql_query=explanations_query)
        explanations = explanations_df.collect()
        self.logger.info("Completed query execution in {} ms".format(
            DateTimeUtil.current_milli_time()-start_time))

        fields = explanations_df.columns
        values, total_count = self.__get_values_and_total_count(
            explanations=explanations, fields=fields, limit=limit, offset=offset, include_total_count=include_total_count,
            search_filters=search_filters)

        return fields, values, total_count

    def __get_explanations_query(self, limit=None, offset=None,
                                 column_filters=None,
                                 search_filters=None,
                                 order_by_column=None):
        str_col_filters = ",".join(
            ["\"" + f + "\"" for f in column_filters.split(",")]) if column_filters else "*"

        conditions = self.__get_conditions_from_search_filters(search_filters)

        query = "SELECT {} FROM \"{}\".\"{}\" WHERE {}".format(
            str_col_filters, self.schema_name, self.table, conditions)

        if order_by_column:
            fs = order_by_column.split(":")
            query = "{} ORDER BY \"{}\" {}".format(
                query, fs[0], fs[1].upper())

        if limit:
            limit = min(limit, 100)
            query = "{} LIMIT {}".format(query, limit)

        if offset:
            query = "{} OFFSET {}".format(query, offset)

        return query

    def __get_total_count_query(self, search_filters):
        conditions = self.__get_conditions_from_search_filters(search_filters)
        return "SELECT COUNT(*) AS explanations_count FROM \"{}\".\"{}\" WHERE {}".format(
            self.schema_name, self.table, conditions)

    def __get_values_and_total_count(self, explanations, fields, limit=None, offset=None, include_total_count=None, search_filters=None):
        values = []
        total_count = 0
        for row in explanations:
            values_row = []
            for f in fields:
                val = row[f]
                if val and isinstance(val, datetime):
                    val = DateTimeUtil.get_datetime_iso_format(val)
                if val and isinstance(val, bytearray):
                    val = val.decode("utf-8")
                values_row.append(val)
            values.append(values_row)

        if include_total_count:
            if len(values) < limit and offset is not None and int(offset) == 0:
                total_count = len(values)
            else:
                total_count_query = self.__get_total_count_query(
                    search_filters)
                start_time = DateTimeUtil.current_milli_time()
                self.logger.info(
                    "Executing query {}.".format(total_count_query))
                rows = DbUtils.get_table_as_dataframe(spark=self.spark,
                                                      location_type=self.location_type,
                                                      database_name=self.database,
                                                      schema_name=self.schema_name,
                                                      table_name=self.table,
                                                      connection_properties=self.connection_properties,
                                                      sql_query=total_count_query).select("explanations_count").collect()
                self.logger.info("Completed query execution in {} ms".format(
                    DateTimeUtil.current_milli_time()-start_time))
                total_count = rows[0][0]
                self.logger.info("total count {}".format(total_count))

        return values, total_count

    def __get_conditions_from_search_filters(self, search_filters):
        conditions_str = ""
        if search_filters:
            conditions = []
            filters = search_filters.split(",")
            for f in filters:
                fs = f.split(":")
                column = fs[0]
                operator = fs[1]
                value = ":".join(fs[2:])
                if operator == "eq":
                    conditions.append("\"{}\"='{}'".format(column, value))
                elif operator == "in":
                    values = ",".join(["'{}'".format(x)
                                       for x in value.split(",")])
                    conditions.append("\"{}\" IN ({})".format(column, values))
                elif operator == "le":
                    conditions.append("\"{}\" <= '{}'".format(column, value))
                elif operator == "ge":
                    conditions.append("\"{}\" >= '{}'".format(column, value))

            if conditions:
                conditions_str = " AND ".join(conditions)

        return conditions_str
