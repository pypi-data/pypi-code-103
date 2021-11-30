# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import datetime
import json
import os
import pyspark.sql.functions as F
from ibm_wos_utils.joblib.tests.base_test_utils import BaseTestUtils
from ibm_wos_utils.joblib.utils.date_util import DateUtil
from ibm_wos_utils.joblib.utils.db_utils import DbUtils, JDBCUtils
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils.dialect_utils import DialectUtils

from pyspark.sql import SparkSession
from pyspark import SparkContext

spark = SparkSession \
    .builder\
    .appName("DbUtils") \
    .getOrCreate()


class TestDbUtils(BaseTestUtils):

    @classmethod
    def setUpClass(cls):
        pass

    def test_read_data_from_db2(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = "com.ibm.db2.jcc.DB2Driver"

        ssl_certificate = None
        use_ssl = False
        # Read certificate from file in case of SSL connection
        '''
        file_path = os.path.abspath(os.getcwd()) + \
                                    "/ibm_wos_utils/joblib/tests/ssl_cert.txt"
        with open(file_path,"r") as f:
            ssl_certificate = f.read()
        use_ssl=True
        '''
        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver, use_ssl=use_ssl, ssl_certificate=ssl_certificate)
        probability_column = "probability"
        try:
            df = DbUtils.get_table_as_dataframe(spark,
                                                "jdbc",
                                                database_name,
                                                table_name,
                                                schema_name=schema_name,
                                                connection_properties=connection_properties,
                                                probability_column=probability_column
                                                )
            row_count = df.count()
            assert df is not None and row_count > 0
            self.validate_probability_column(df, probability_column)
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))
        finally:
            # Delete certificate file in case of SSL
            DbUtils.delete_certificate_file(
                connection_properties=connection_properties)

    def test_read_data_from_db2_with_timestamp(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        record_timestamp_column = "scoring_timestamp"

        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url)
        df = DbUtils.get_table_as_dataframe(spark,
                                            "jdbc",
                                            database_name,
                                            table_name,
                                            schema_name=schema_name,
                                            connection_properties=connection_properties,
                                            record_timestamp_column=record_timestamp_column,
                                            start_time=str(
                                                datetime.datetime.utcnow().isoformat() + 'Z')
                                            )
        # The start date is current time, so it should return empty dataframe
        assert df is not None
        assert df.count() == 0

        df = DbUtils.get_table_as_dataframe(spark,
                                            "jdbc",
                                            database_name,
                                            table_name,
                                            schema_name=schema_name,
                                            connection_properties=connection_properties,
                                            record_timestamp_column=record_timestamp_column,
                                            end_time="2020-01-21T00:00:00.00Z"
                                            )
        # The end date is earlier than table creation time, so it should return empty dataframe
        assert df is not None
        assert df.count() == 0

    def test_read_data_from_db2_invalid_driver(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = "test_driver"

        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver)
        try:
            df = DbUtils.get_table_as_dataframe(spark,
                                                "jdbc",
                                                database_name,
                                                table_name,
                                                schema_name=schema_name,
                                                connection_properties=connection_properties
                                                )
        except DatabaseError as clerr:
            assert "Specified JDBC driver '{}' could not be found".format(
                driver) in str(clerr)

    def test_hive_jdbc(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        jdbc_url = "jdbc:hive2://<host>:10000/<database_name>"
        driver = "org.apache.hive.jdbc.HiveDriver"

        connection_properties = DbUtils.get_connection_properties(
            None, None, jdbc_url, driver)
        try:
            df = DbUtils.get_table_as_dataframe(
                spark,
                "jdbc",
                database_name,
                table_name,
                schema_name=schema_name,
                connection_properties=connection_properties,
                probability_column="probability"
            )
            row_count = df.count()
            assert df is not None and row_count > 0
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))
        finally:
            # Delete certificate file in case of SSL
            DbUtils.delete_certificate_file(connection_properties)

    def test_hive_jdbc_list_columns(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        jdbc_url = "jdbc:hive2://<host>:10000/<database_name>"
        driver = "org.apache.hive.jdbc.HiveDriver"

        connection_properties = DbUtils.get_connection_properties(
            None, None, jdbc_url, driver)
        probability_column = "probability"
        try:
            columns = DbUtils.list_columns(
                spark,
                "jdbc",
                database_name,
                table_name,
                schema_name=schema_name,
                connection_properties=connection_properties,
                probability_column=probability_column
            )
            assert columns is not None and len(columns) > 0
            # Assert that probability column is an array
            for column in columns:
                if column.name == probability_column:
                    assert column.dataType == "array<double>"
                    break
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))
        finally:
            # Delete certificate file in case of SSL
            DbUtils.delete_certificate_file(connection_properties)

    def test_dialect(self):
        DialectUtils.register_hive_dialect(spark)

    def test_write_df_to_db2(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = "com.ibm.db2.jcc.DB2Driver"
        probability_column = "probability"
        timestamp_column = "scoring_timestamp"
        try:
            connection_properties = DbUtils.get_connection_properties(
                user, password, jdbc_url, driver)
            # Read data from CSV
            df = self.read_csv_resource_as_spark_df(
                "gcr_feedback.csv", spark)
            assert df is not None
            import pyspark.sql.functions as F
            df = df.withColumn(
                probability_column,
                F.split(
                    F.col(probability_column), '\|').cast("array<double>"))
            df.printSchema()
            df_sub = df.limit(10)
            # assign current timestamp value
            current_ts = DateUtil.get_current_datetime()
            start_time = DateUtil.get_datetime_as_str(current_ts)
            df_sub = df_sub.withColumn("scoring_timestamp",
                                       F.when(df_sub["scoring_timestamp"] != current_ts, current_ts).otherwise(df_sub['scoring_timestamp']))
            # Write dataframe to table
            DbUtils.write_dataframe_to_table(
                df_sub, 'jdbc',
                database_name, table_name, schema_name=schema_name,
                connection_properties=connection_properties, probability_column='probability')

            # Verify that rows are added to the table
            df = DbUtils.get_table_as_dataframe(
                spark,
                "jdbc",
                database_name,
                table_name,
                schema_name=schema_name,
                connection_properties=connection_properties,
                record_timestamp_column=timestamp_column,
                start_time=start_time
            )
            assert df is not None
            row_count = df.count()
            assert row_count == df_sub.count()

        except Exception as e:
            assert False, "Failed to write dataframe to DB2 using JDBC. Error: {}".format(
                str(e))

    def test_read_data_from_db2_with_empty_driver(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        # Test with empty string as driver input
        driver = ""

        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver)
        try:
            df = DbUtils.get_table_as_dataframe(spark,
                                                "jdbc",
                                                database_name,
                                                table_name,
                                                schema_name=schema_name,
                                                connection_properties=connection_properties,
                                                probability_column="probability"
                                                )
            row_count = df.count()
            assert df is not None and row_count > 0
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))

        # Test with None as driver input
        driver = None
        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver)
        try:
            df = DbUtils.get_table_as_dataframe(spark,
                                                "jdbc",
                                                database_name,
                                                table_name,
                                                schema_name=schema_name,
                                                connection_properties=connection_properties,
                                                probability_column="probability"
                                                )
            row_count = df.count()
            assert df is not None and row_count > 0
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))

    def validate_probability_column(self, df, probability_column):
        first_row = df.limit(1).select(probability_column).collect()
        if first_row is not None and len(first_row) > 0:
            prob_val = first_row[0][0]
            assert type(prob_val) is list, \
                "Probability column type is not array."
            assert len(prob_val) > 1, "Probability array contains single value."

    def test_db2_case_sensitivity(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = "com.ibm.db2.jcc.DB2Driver"

        ssl_certificate = None
        use_ssl = False
        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver, use_ssl=use_ssl, ssl_certificate=ssl_certificate)
        # Specify column names in expected case. If not specified, they will be read in the case in which they are stored in database
        columns_to_map = ["age", "sex", "checkingstatus", "risk"]
        try:
            df = DbUtils.get_table_as_dataframe(
                spark,
                "jdbc",
                database_name,
                table_name,
                schema_name=schema_name,
                connection_properties=connection_properties,
                columns_to_map=columns_to_map)
            assert df is not None
            # Verify that the columns in dataframe are returned in expected case
            for col in columns_to_map:
                assert col in df.columns
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))
        finally:
            # Delete certificate file in case of SSL
            DbUtils.delete_certificate_file(
                connection_properties=connection_properties)

    def test_write_to_non_existing_table(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = "com.ibm.db2.jcc.DB2Driver"
        try:
            connection_properties = DbUtils.get_connection_properties(
                user, password, jdbc_url, driver)
            cols = ['NAME', 'AGE']
            df = spark.createDataFrame(
                [('A', 20), ('B', 25)]).toDF(*cols)
            df.printSchema()
            DbUtils.write_dataframe_to_table(
                df, 'jdbc',
                database_name, table_name, schema_name=schema_name,
                connection_properties=connection_properties, spark=spark)
            assert False, "Should not write to non-existing table."
        except DatabaseError as e:
            assert "Table {}.{} could not be found in the database.".format(
                schema_name, table_name) in str(e)

    def test_read_data_from_empty_table(self):
        # Enter database details
        database_name = ""
        table_name = ""
        schema_name = ""
        user = ""
        password = ""
        jdbc_url = "jdbc:db2://<host>:<port>/<database_name>"
        driver = ""

        use_ssl = False
        ssl_certificate = ""

        connection_properties = DbUtils.get_connection_properties(
            user, password, jdbc_url, driver, use_ssl=use_ssl, ssl_certificate=ssl_certificate)
        probability_column = "probability"
        columns_to_map = ["pickup_weekday", "pickup_hour"]
        try:
            df = DbUtils.get_table_as_dataframe(
                spark,
                "jdbc",
                database_name,
                table_name,
                schema_name=schema_name,
                connection_properties=connection_properties,
                columns_to_map=columns_to_map,
                probability_column=probability_column
            )
            assert df is not None
            assert df.columns is not None and len(df.columns) > 0
            if probability_column:
                prob_col_type = dict(df.dtypes).get(probability_column)
                assert prob_col_type == "array<double>"
            row_count = df.count()
            assert row_count == 0
        except Exception as e:
            assert False, "Failed to read data from DB2 using JDBC. Error: {}".format(
                str(e))
        finally:
            # Delete certificate file in case of SSL
            DbUtils.delete_certificate_file(
                connection_properties=connection_properties)

if __name__ == '__main__':
    unittest.main()
