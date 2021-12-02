import ctypes
from .global_constants import *

class TIMESTAMP(ctypes.Structure):
        _fields_ = [('datetime', ctypes.c_size_t),
                ('milliseconds', ctypes.c_int)]
            
class HEADER(ctypes.Structure):
        _fields_ = [('ticker_symbol', ctypes.c_char * 6),
                ('record_count', ctypes.c_long),
                ('beginning_timestamp', TIMESTAMP),
                ('ending_timestamp', TIMESTAMP),
                ('checksum', ctypes.c_longlong)
                ]
                
class TickFile():        
        def __init__(self, file_path):
                chartoscope_dll = ctypes.cdll.LoadLibrary(GlobalConstants.default_lib_path)

                tick_file = chartoscope_dll.PyTickFile_init()
                                
                encoded_path = file_path.encode('utf-8')

                chartoscope_dll.PyTickFile_open_for_reading(tick_file, ctypes.c_char_p(encoded_path))
                chartoscope_dll.PyTickFile_header.restype = ctypes.c_void_p

                self.header = HEADER.from_address(chartoscope_dll.PyTickFile_header(tick_file))
