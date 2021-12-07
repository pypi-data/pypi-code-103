# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: May 09, 2018
# Modified: Apr 21, 2021

# Import system standard modules
import json

from siki.basics import FileUtils as fileutil
from siki.basics import Convert as convert


def decode_json(string: str):
    """
    Load data from json file

    @Args: 
    * [filename] filename with path  

    @Returns:  
    * [dict] if load success. None, failed, empty data
    """
    if string:
        try:
            return json.loads(string)

        except Exception as e:
            print(e)
            return None

    return None


def encode_json(data: object):
    """
    any python object that can be encode to json string

    @Args:
    * [data] list, dict

    @Returns:
    * [str] if convert success, else is None
    """
    if data:
        try:
            return json.dumps(data)

        except Exception as e:
            print(e)
            return None

    return None


def load_json_file(filename: str):
    """
    Create a blank file or load data from json file

    @Args:
    * [filename] (str), filename with path
    
    @Returns:  
    *[dict] if load success. None, failed, empty data
    """
    # load json file from given filename
    raw = fileutil.read_file(filename)
    if raw:
        return decode_json(convert.binary_to_string(raw))
    else:
        return {}


def write_json_file(dictionary: dict, filename: str):
    """
    Write dictionary to json file
    
    @Args: 
    * [dictionary] (dict), key value pairs  
    * [filename] (str), filename with path  
    """
    if len(dictionary) > 0:
        raw = convert.string_to_binary(json.dumps(dictionary))
        fileutil.write_file(filename, raw)
