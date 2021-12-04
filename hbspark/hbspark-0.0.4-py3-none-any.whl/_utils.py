"""
A class holding common utility functions for hbspark
"""

from pyspark.sql import Row

#Create hbase row from "columnfamiliy:column" : "value"
def hbase_row(dictionary):
    """
    Creates a new U{spark.sql.Row<https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.Row.html>} given an input dict
    """
    new_row = Row(**dictionary)
    return new_row

# Conversion from SO: https://stackoverflow.com/questions/33137741/fastest-way-to-convert-a-dicts-keys-values-from-bytes-to-str-in-python3
def bindict_to_strdict(data):
    """
    Converts a binary dictionary into a matching string dictionary.

    Used to decode thrift API responses.
    
    @type data: dict
    @param data: A dictionary with binary keys / values to be convereted into C{string} dictionary.

    @rtype: dict
    @return: The new string dictionary.
    """
    if isinstance(data, bytes):  return data.decode('utf-8')
    if isinstance(data, dict):   return dict(map(bindict_to_strdict, data.items()))
    if isinstance(data, tuple):  return map(bindict_to_strdict, data)
    if isinstance(data, list):   return list(map(bindict_to_strdict, data))
    return data

def binlist_to_strlist(data):
    """
    Converts a binary list into a matching string list.

    Used to decode thrift API responses.

    @type data: list
    @param data: A list with binary values to be convereted into C{string} list.

    @rtype: list
    @return: The new list of strings.
    """
    # print(type(data))
    if isinstance(data, bytes): return data.decode('utf-8')
    if isinstance(data, list): return list(map(binlist_to_strlist, data))
    if isinstance(data, tuple): return map(binlist_to_strlist, data)
    return data