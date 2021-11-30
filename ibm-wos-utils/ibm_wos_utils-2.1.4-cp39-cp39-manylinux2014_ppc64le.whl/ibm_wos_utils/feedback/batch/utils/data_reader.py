# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.sql.functions import col, expr
except ImportError as ie:
    pass

from datetime import datetime

class DataReader():

    
    def __init__(self, logger):
        self.logger = logger
    
    '''
    Reads the data based on the last run updated timestamp and minimum sample size. 
    These are the various scenario's handled to fetch the data
    Case 1. Timestamp column and min_sample_size are not present then fetch all the data from the table
            case1 will not be considered as the timestamp column is manadatory in the common config notebook
    Case 2. Timestamp column and min_sample_size are present but there are no records in the timestamp 
            then throw the exception saying that the timestamp values are empty.
    case 3. Timestamp column is present but min_records is not present then fetch all the records after 
            the last processed time
    case 4. Timestamp column is present(values exists) and min_sample_size is given then fetch the records count from
            the last processed time to current time. If the records count is less than min_sample_size then throw 
            the exception otherwise fetch the all the data from the table
    '''

    def read_data(self, spark, scoring_id_col, label_col, prediction_col, connection_props, 
                    timestamp_col=None, last_updated_timestamp=None, min_sample_records=0):

        table_name = connection_props['table_name']
        db_name = connection_props['db_name']
        storage_type = connection_props['type']
        is_skip_header_defined = False
        sample_size = int(min_sample_records)
        
        if storage_type == "hive":
            is_skip_header_defined, sql_query = self.get_sql_query_tbl_properties(spark, db_name,
                                                table_name, scoring_id_col)
            
        if not is_skip_header_defined:
            sql_query = "select * from {}.{}".format(db_name, table_name)
        
        spark_df = spark.sql(sql_query)
        is_timestamp_val_set = False
        err_msg = "Quality Run Execution Failed. Error: "

        if timestamp_col is not None:
            timestamp_col_values = spark_df.filter(col(timestamp_col).isNotNull()).count()
            if timestamp_col_values == 0:
                mesg = "{} Timestamp values are required in `{}` column to compute the quality metrics".format(err_msg, timestamp_col)
                raise Exception(mesg)
    
        if timestamp_col is not None and last_updated_timestamp is not None:
            self.logger.info("Filtering the data based on the last processed timestamp {}".format(
                last_updated_timestamp))

            if timestamp_col_values > 0:
                last_updated_timestamp = self.get_database_date_format(last_updated_timestamp)
                #fetch the records based on the previous run finished time
                spark_df = spark_df.filter(
                    spark_df[timestamp_col] > last_updated_timestamp)
                is_timestamp_val_set = True
                spark_df.show()
            
        self.logger.info("Fetching the count of the records from the table {}".format(table_name))
        #ignore nulls in the label and prediction column's
        spark_df = spark_df.dropna(subset=[label_col, prediction_col])
        records_count = spark_df.count() 
        
        if sample_size > 0:    
            if records_count < sample_size:
                if is_timestamp_val_set:
                    current_time = self.get_current_time()
                    msg = "{} Records count {} in the timeframe ({} - {}) are less than min sample size {}"\
                                .format(err_msg, records_count, last_updated_timestamp, current_time, sample_size)
                else:
                    msg = "{} Records count {} are less than min sample size {}".format(err_msg, records_count, sample_size)
                raise Exception(msg)
            
            '''
            #Revisit the below logic  to get the delta records from the previous run
            if is_timestamp_val_set and records_count < sample_size:
                self.logger.info("Records count {} are less than Sample size {}".format(records_count, sample_size))
                spark_df = spark.sql(sql_query)
                spark_df = spark_df.orderBy(timestamp_col, ascending=False)
                spark_df = spark_df.limit(sample_size)
                records_count = spark_df.count()
                timestamp_first = spark_df.select(timestamp_col).first()
                if records_count < sample_size:
                    raise Exception("There are no sufficient records in the table to process the quality computation")
          '''
        else:
            if records_count == 0:
                if is_timestamp_val_set: 
                    msg = "{} There are no new records in the table '{}' after the last processed time '{}' to compute the quality metrics" \
                            .format(err_msg,table_name, last_updated_timestamp)
                else:
                    msg = "{} There are no records in the table '{}' to compute the quality metrics".format(err_msg, table_name)
                raise Exception(msg)
        
        self.logger.info("Printing the table column datatypes")
        self.logger.info(spark_df.dtypes)
        self.logger.info("Number of records {} in the table".format(records_count))
        return spark_df, records_count

    def get_database_date_format(self, last_run_timestamp):
        formatted_date = last_run_timestamp
        if last_run_timestamp is not None:
            #This is the time format saved in quality runs
            last_run_date  = datetime.strptime(last_run_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            #convert the date to database timestamp format
            #This is the default format "YYYY-MM-DD HH:MM:SS.fffffffff" supported by the database 
            formatted_date =  datetime.strftime(last_run_date, "%Y-%m-%d %H:%M:%S.%f")
        
        return formatted_date
    
    def get_current_time(self):
        
        current_time = datetime.utcnow()
        formatted_date =  datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S.%f")

        return formatted_date

    def get_sql_query_tbl_properties(self, spark, db_name, table_name, scoring_id_col):
        
        is_skip_header_defined = False
        sql_query = None

        table_properties = spark.sql("show tblproperties {}.{}".format(
                        db_name, table_name)).collect()
        property_keys = [row.key for row in table_properties]
        if ("skip.header.line.count" in property_keys):
            self.logger.info(
                    "Property skip.header.line.count present in table_properties. Will discard first row.")
    
            # NVL function in select query will use this string when the scoring_id value is null. 
            # `not_matching_string` value should not match with any of the scoring id value, 
            # hence updated the string with special characters.
            not_matching_string = "&*%^#@@~({)/><?;}+-"
            # Fetches all the rows from the table except the first row irrespective of whether 
            # the scoring_id col value is empty or not.
            sql_query = "select * from {}.{} where NVL({}, \"{}\") != \"{}\"".format(db_name, 
                        table_name, scoring_id_col, not_matching_string, scoring_id_col)
            is_skip_header_defined = True
        
        return is_skip_header_defined, sql_query
