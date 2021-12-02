import os
# on windows, add the package folder to the dll search path
script_folder = os.path.dirname(os.path.realpath(__file__))
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(script_folder)

from .pyreadr import read_r, list_objects, write_rds, write_rdata, download_file
from .custom_errors import PyreadrError, LibrdataError

__version__ = "0.4.4"


