"""Reading contents of binary files exported using `expdb`

This module reads the BinExport dataclass from the binary file
exported using `expdb` library
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pickle
from typing import Union
from dataclasses import asdict
from expdb.data.models import BinExport

class ReadBin():
    """Class for reading binary exports
    
    Attributes
    ----------
    filepath : str
        Path of binary file to read
    
    Methods
    -------
    read(_asdict = False)
        Read the binary file
    """

    def __init__(self, filepath: str):
        """
        Parameters
        ----------
        filepath : str
            Path of binary file to be read
        """
        self.file = filepath

    def read(self, _asdict: bool = False) -> Union[BinExport, dict, bool]:
        """Read the BinExport dataclass from `.dat` binary file export
        
        Parameters
        ----------
        _asdict : bool, optional
            Read binary file as a dictionary
        
        Returns
        -------
        BinExport
            BinExport dataclass instance
        dict
            Dictionary with dataclass values
        bool
            False if any error occurs
        """
        try:
            if os.path.isfile(self.file):
                with open(self.file, mode = "rb") as import_file:
                    DATA = pickle.load(import_file)
                if _asdict is True:
                    return asdict(DATA)
                else:
                    return DATA

            else:
                return False

        except:
            return False
