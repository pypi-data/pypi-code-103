# _hb_session.py
# Internal session tracking and api interfaces
# Kris Zhao

###################
#     Imports     #
###################
from pyspark.sql import Row

############################
#     Global Variables     #
############################
conn = None             # Store the HappyBase Connection Instance
spark_session = None    # Store the spark session (for DF creation)

###################
#     Methods     #
###################
# Load the variables into the session
def init(connection, spark):
    global conn
    conn = connection

    global spark_session
    spark_session = spark

# Check if the connection and session have been initialized
# Returns boolean
def isInitialized():
    return conn != None and spark_session is not None

# Get the HB connection from the session
def connection():
    return conn

# Get the spark_session from the session
def spark():
    return spark_session

# Create spark dataframe from dicts / lists
# Returns spark dataframe
def create_data_frame(val, schema=None, samplingRatio=None, verifySchema=True):
    return spark_session.createDataFrame(val, schema, samplingRatio, verifySchema)

# Create a new spark Row
# Returns a spark row
def create_row(*args, **kwargs):
    return Row(*args, **kwargs)

# Creates a HBase table through HappyBase
# Returns nothing
def _create_table(name, families):
    return conn.create_table(name, families)

# Delete a HBase table through happybase Table
# Should return nothing
def _delete_table(name, disabled):
    return conn.delete_table(name, disabled)

# Query the Happybase API by function name, and args / kwargs
# Returns whatever is returned by the function.
def query(hb_function, *args, **kwargs):
    if(isInitialized()):
        return getattr(conn, hb_function)(*args, **kwargs)
    
    return None