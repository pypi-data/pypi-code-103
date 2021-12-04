"""
C{hbspark} is an simple to use data pipepline, moving data stored inside HBase into C{pyspark} for distributed computation using HBase's Thrift API.
"""
# Import main api
import happybase as hb

#####################################################
#      Link to other distributed functionality      #
#####################################################
# Global session management
# Holds the spark session as well as open happybase connection
from . import _hb_session as hb_session

# Tables management functionality:
from .table import *

# General utilitarian functions
from ._utils import *

# Function to initialize the connection:
# Built off hostname, and the spark_session.

def connect(hostname, spark_session):
    """
    Connect the HBase hostname to the provided spark session.

    @type hostname: string
    @param hostname: The hostname or IP of the HBase thrift gateway.

    @type spark_session: pyspark.sql.SparkSession
    @param spark_session: The instantiated spark session used to create dataframes.
    
    @rtype: None
    @return: Method has no return
    """
    hb_session.init(hb.Connection(hostname), spark_session)