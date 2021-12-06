"""config

This module controls the fetching and caching of the config file

It exports the following functions:
 * get_config(index=None, filename="./config.json")
    -> returns the config dictionary (at the specified index if it
        is specified) and loads & caches it if needed

It also consists of the following internal functions:
 * fetch_config(filename="./config.json")
    -> returns the config dictionary and loads & caches it if needed
"""

import json

from typing import Any, Dict

config_cache: Dict = None

def fetch_config(filename="./config.json") -> Dict:
    """
    Fetches and caches the configuration file.

    The file should be a JSON file.

    NOTE:
        This function is intended to load a SINGLE configuration file throughout a program's
        lifespan. This means it will used the cached configuration file even if the filepath
        is different!

    Parameters
    ----------
    filename : str
        Throws FileNotFoundError if the file does not exist.

    Returns
    -------
    object
        The configuration object

    """
    global config_cache
    if config_cache is not None:
        return config_cache

    with open(filename, 'r', encoding="UTF-8") as file:
        data = json.load(file)
        config_cache = data
        return data

def get_config(index=None, filename="./config.json") -> Any:
    """
    Wraps fetch_config with the ability to index the given configuration.

    Parameters
    ----------
    index : str
        The key in the config to index and return

    filename : str
        The path to the config file


    Returns
    -------
    any
        The configuration object/value
    """
    config = fetch_config(filename)

    if index is not None:
        if index not in config:
            return None
        return config[index]
    return config
