#! python3
import configparser
import os
from ..defaults.default_config import set_defaults
from collections import defaultdict

def parse_config2(filename=None):
    """
    https://docs.python.org/3.5/library/configparser.html
    :param filename: filename to parse config
    :return: config_parse result
    """

    _config = configparser.ConfigParser(allow_no_value=True)

    if filename:
        # ConfigParser does not create a file if it doesn't exist, so I will create an empty one.
        if not os.path.isfile(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                print('', file=f)

        _config.read_file(open(filename))

    return _config

def get_common_config_dict(filename=None):
    """
    Main function to get the configs from config file
    :param filename: filename to parse
    :return: only common section content in dict 
    """
    _config_parse_obj = get_all_config(filename=filename) # type: object
    _options = defaultdict(dict) # type: dict

    # Use general section for general options:
    if _config_parse_obj.has_section('common'):
        for key in _config_parse_obj['common']:
            # convert string to tuple in case of list of columns
            if key == 'csv_export_headers':
                _options[key] = eval(_config_parse_obj['common'][key])
            else:
                _options[key] = _config_parse_obj['common'][key]
    else:
        _options = {}

    return _options

def get_all_config(filename=None):
    """
    Set default configuration options for configparse
    Config with defaults settings if no file will be passed
    Also with defaults sections and defaults keys for missing options in config
    :param filename: options config file to read
    :return: configparser object with default config for missing sections
    """

    _config = parse_config2(filename)
    default_config = set_defaults()

    # Verify each section in default_config
    for s in range(len(default_config.sections())):
        section = default_config.sections()[s]

        # Add the missing section to the config obtained
        if not _config.has_section(section):
            _config.add_section(section)

        # Add missing keys to config obtained
        for key in default_config[section]:
            if not _config.has_option(section, key):
                _config[section][key] = default_config[section][key]

    return _config
