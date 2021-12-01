"""
This configuration file is used to define the expected structure of the data packets

Contents are defined in order of appearance and have a number of bytes associated with them
"""

import platform
import pathlib
import logging
import datetime
from enum import Enum

#=====================================================================================================================
#                              PACKET FORMAT CONFIGURATION
#=====================================================================================================================
class Packet(Enum):
    #=====================================================================================
    # define modified enum class to handle multiple attribute assignment
    # DO NOT MODIFY
    def __init__(self, field_name, number_of_bytes):
        self.field_name = field_name
        self.number_of_bytes = number_of_bytes
    #=====================================================================================
    """
    The order of appearance of these fields should match the expected format of the RATS .txt file
    the Enum property names SHOULD NOT be changed
    
    Attribute format; PROPERTY = field_name, number_of_bytes
    """
    PROTOCOL = "rats_gds_protocol_version", 1
    PAYLOAD_SIZE = "payload_size", 1
    PACKET_COUNT = "packet_count", 2
    TIME_STAMP = "time", 6
    SAMPLE_RATE = "rats_sample_rate", 2
    LLC_COUNT = "llc_trigger_count", 4
    FUNCTION = "function_number", 2
    SAMPLE = "sample_number", 2
    BARCODE_HASH = "barcode_hash", 4
    RETENTION_TIME = "retention_time", 4
    RESERVED = "reserved", 2
    ACTIVE_EDBS = "EDB", 2

    # ============================================================
    DATA = "data", 0 # Do not modify the order or size of this entry



#=====================================================================================================================
#                              LLC CONFIGURATION
#=====================================================================================================================

#   ON WHICH EDB DO WE EXPECT TO FIND THE LLC STATES, THIS IS UNLIKELY TO CHANGE, SO DON'T MESS WITH THIS
LLCEDB = 1

class LLCEDBFormat(Enum):
    """
    CHANGE THE ENUM PROPERTY NAMES TO DEFINE THE ACTIVE LLCS. ANY PROPERTY WITH 'BIT' IN ITS NAME WILL NOT BE STORED
    BY THE PARSING OPERATION
    """
    BIT0 = 0
    BIT1 = 1
    BIT2 = 2
    BIT3 = 3
    BIT4 = 4
    BIT5 = 5
    BIT6 = 6
    BIT7 = 7
    BIT8 = 8
    BIT9 = 9
    SIP = 10
    BIT11 = 11
    BUFFIS = 12
    BIT13 = 13
    BIT14 = 14
    BIT15 = 15

#=====================================================================================================================
#                              FILE PATH CONFIGURATION
#=====================================================================================================================
if platform.system() == 'Windows':
    splitchar = '\\'
    cachepath = '\\cache\\'
    dfpath = '\\feathereddataframes\\'
    figurepath = '\\pickledfigures\\'
    topopath = '\\topo\\'
    logs = '\\logs\\'
else:
    splitchar = '/'
    cachepath = '/cache/'
    dfpath = '/feathereddataframes/'
    figurepath = '/pickledfigures/'
    topopath = '/topo/'
    logs = '/logs/'

packagepath = pathlib.Path(__file__).parent.parent.resolve()


#=====================================================================================================================
#                              LOG FILE CONFIGURATION
#=====================================================================================================================
log_date = datetime.datetime.now().strftime("%d%b%Y")

logging.basicConfig(filename=f'{str(packagepath)+logs+log_date}ratslog.log', encoding='utf-8',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
